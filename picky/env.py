from __future__ import print_function

from collections import OrderedDict
from difflib import unified_diff

from .oyaml import safe_load, safe_dump


class PackageSpec(object):

    def __init__(self, sep, name, version=None, build=None):
        self.sep = sep
        self.name = name
        self.version = version
        self.build = build

    def __str__(self):
        return self.sep.join(e for e in (self.name, self.version, self.build)
                             if e is not None)


class Environment(dict):

    @classmethod
    def from_string(cls, yaml):
        data = safe_load(yaml) or {}
        conda = OrderedDict()
        pip = OrderedDict()
        develop = OrderedDict()
        for spec in data.get('dependencies', ()):
            if isinstance(spec, dict):
                for pip_spec in spec['pip']:
                    if pip_spec.startswith('-e'):
                        e, path = pip_spec.split()
                        develop[path] = PackageSpec(' ', e, path)
                    else:
                        name, version = pip_spec.split('==')
                        pip[name] = PackageSpec('==', name, version)
            else:
                parts = spec.split('=', 2)
                conda[parts[0]] = PackageSpec('=', *parts)
        return cls(
            name=data.get('name'),
            channels=data.get('channels', ()),
            conda=conda,
            pip=pip,
            develop=develop,
        )

    @classmethod
    def from_path(cls, path):
        with open(path) as source:
            return cls.from_string(source.read())

    def to_string(self):
        output = OrderedDict()
        name = self.get('name')
        if name:
            output['name'] = name
        output['channels'] = self['channels']
        output['dependencies'] = deps = []
        for spec in self['conda'].values():
            deps.append(str(spec))
        pip_specs = self.get('pip')
        develop_specs = self.get('develop')
        if pip_specs or develop_specs:
            pip_deps = []
            deps.append({'pip': pip_deps})
            for spec in pip_specs.values():
                pip_deps.append(str(spec))
            for spec in develop_specs.values():
                pip_deps.append(str(spec))
        return safe_dump(output, default_flow_style=False)

    def copy(self):
        return type(self)(
            name=self['name'],
            channels=list(self['channels']),
            conda=self['conda'].copy(),
            pip=self['pip'].copy(),
            develop=self['develop'].copy(),
        )


def modify(env, ignore=None, develop=None):
    env = env.copy()
    if ignore:
        for type in 'conda', 'pip':
            for key in ignore.intersection(env[type]):
                del env[type][key]
    if develop:
        for name, path in develop.items():
            if name in env['pip']:
                del env['pip'][name]
            env['develop'][path] = PackageSpec(' ', '-e', path)
    return env


def diff(expected, actual):
    envs = []
    for env in expected, actual:
        env = env.copy()
        del env['name']
        envs.append(env.to_string().split('\n'))
    udiff = '\n'.join(unified_diff(
        *envs, lineterm='', fromfile='expected', tofile='actual'
    ))
    if udiff:
        print('Expected environment does not match actual:')
        print(udiff)
    return 1 if udiff else 0

from collections import OrderedDict

from .oyaml import safe_load, dump


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
        data = safe_load(yaml)
        conda = OrderedDict()
        pip = OrderedDict()
        for spec in data['dependencies']:
            if isinstance(spec, dict):
                for pip_spec in spec['pip']:
                    name, version = pip_spec.split('==')
                    pip[name] = PackageSpec('==', name, version)
            else:
                name, version, build = spec.split('=', 2)
                conda[name] = PackageSpec('=', name, version, build)
        return cls(
            name=data['name'],
            channels=data['channels'],
            conda=conda,
            pip=pip,
        )

    @classmethod
    def from_path(cls, path):
        with open(path) as source:
            return cls.from_string(source.read())

    def to_string(self):
        output = OrderedDict()
        output['name'] = self['name']
        output['channels'] = self['channels']
        output['dependencies'] = deps = []
        for spec in self['conda'].values():
            deps.append(str(spec))
        pip_specs = self.get('pip')
        if pip_specs:
            pip_deps = []
            deps.append({'pip': pip_deps})
            for spec in pip_specs.values():
                pip_deps.append(str(spec))
        return dump(output, default_flow_style=False)



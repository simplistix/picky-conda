from collections import namedtuple
from .oyaml import safe_load


class PackageSpec(object):

    def __init__(self, name, version, build=None):
        self.name = name
        self.version = version
        self.build = build


class Environment(dict):
    pass


def parse(text):
    data = safe_load(text)
    conda = []
    pip = []
    for spec in data['dependencies']:
        if isinstance(spec, dict):
            for pip_spec in spec['pip']:
                name, version = pip_spec.split('==')
                pip.append(PackageSpec(name, version))
        else:
            name, version, build = spec.split('=', 2)
            conda.append(PackageSpec(name, version, build))
    return Environment(
        name=data['name'],
        channels=data['channels'],
        conda=conda,
        pip=pip,
    )

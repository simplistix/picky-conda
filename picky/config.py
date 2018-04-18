import os
from argparse import Namespace
from .oyaml import safe_load

VERSION = 'version'
BUILD = 'build'


def parse_config(path):
    if os.path.exists(path):
        with open(path) as source:
            data = safe_load(source)
    else:
        data = {}

    ignore = set(data.get('ignore', ()))
    develop = data.get('develop', {})
    detail = data.get('detail', BUILD)
    return Namespace(
        ignore=ignore,
        develop=develop,
        detail=detail,
    )

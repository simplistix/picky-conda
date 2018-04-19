from argparse import ArgumentParser

from .env import Environment, diff, modify
from .conda import conda_env_export
from .config import BUILD, parse_config


def lock(current_env, concrete_path):
    """
    Lock the current environment's configuration into a
    concrete configuration file on disk.
    """
    with open(concrete_path, 'w') as target:
        target.write(current_env.to_string())


def check(current_env, concrete_path):
    """
    Check if a concrete environment specification matches
    that of the currently activated environment.
    """
    expected_env = Environment.from_path(concrete_path)
    return diff(expected_env, current_env)


def parse_args():
    parser = ArgumentParser(
        description="Manage a concrete environment specification in relation "
                    "to that of the currently activated environment."
    )
    parser.add_argument('--concrete', default='environment.lock.yaml',
                        help=(
                            "Location of the concrete configuration file. "
                            "Defaults to environment.lock.yaml."
                        ))
    parser.add_argument('--config', default='picky.yaml',
                        help=(
                            "Optional picky configuration file. "
                            "Defaults to picky.yaml."
                        ))
    commands = parser.add_subparsers(title='commands')
    for command in lock, check:
        command_parser = commands.add_parser(command.__name__, help=command.__doc__)
        command_parser.set_defaults(func=command)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    config = parse_config(args.config)
    export = conda_env_export(config.detail == BUILD)
    raw_env = Environment.from_string(export)
    current_env = modify(raw_env, config.ignore, config.develop)
    return args.func(current_env, args.concrete)

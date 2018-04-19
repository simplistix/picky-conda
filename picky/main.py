from argparse import ArgumentParser

from .env import Environment, diff, modify
from .conda import conda_env_export
from .config import BUILD, parse_config


def lock(current_env, concrete_path):
    with open(concrete_path, 'w') as target:
        target.write(current_env.to_string())


def check(current_env, concrete_path):
    expected_env = Environment.from_path(concrete_path)
    return diff(expected_env, current_env)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--concrete', default='environment.lock.yaml')
    parser.add_argument('--config', default='picky.yaml')
    commands = parser.add_subparsers()
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

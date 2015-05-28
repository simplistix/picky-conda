from argparse import ArgumentParser

import logging
import sys
from datetime import datetime
from picky.handlers import PipHandler, CondaHandler
from picky.requirements import Diff


def log_level(text):
    level_name = str(text).upper()
    try:
        return getattr(logging, level_name)
    except AttributeError:
        raise TypeError(level_name)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--pip', default='pip')
    parser.add_argument('--conda', default='conda')
    parser.add_argument('--pip-requirements', default='requirements.txt')
    parser.add_argument('--conda-versions', default='conda_versions.txt')
    parser.add_argument('--update', action='store_true')
    parser.add_argument('-l', '--log-level', default='warn', type=log_level)
    args = parser.parse_args()
    return args


def setup_logging(level):
    if level < logging.WARNING:
        template = '%(asctime)-15s %(levelname)-7s %(message)s'
    else:
        template = '%(message)s'
    logger = logging.getLogger()
    formatter = logging.Formatter(template, '%Y-%m-%d %H:%M:%S')
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.setLevel(level)
    handler.setLevel(level)
    logger.addHandler(handler)


def error_and_exit(pip, conda):
    logging.getLogger().error('Neither %s nor %s could be found',
                              pip, conda)
    sys.exit(2)


def exit_with_code(conda_diff, pip_diff):
    if pip_diff or conda_diff:
        exit_code = 1
    else:
        exit_code = 0
    sys.exit(exit_code)


def main():
    args = parse_args()
    setup_logging(args.log_level)
    now = datetime.now()

    pip = PipHandler(args.pip, args.pip_requirements)
    conda = CondaHandler(args.conda, args.conda_versions)

    if not (pip.executable_found or conda.executable_found):
        error_and_exit(args.pip, args.conda)

    conda.used.combine_with(pip.used, now)

    pip_diff = Diff(pip.specified, pip.used)
    conda_diff = Diff(conda.specified, conda.used)

    pip_diff.log()
    conda_diff.log()

    if args.update:
        pip.update(pip_diff, now)
        conda.update(conda_diff, now)

    exit_with_code(conda_diff, pip_diff)

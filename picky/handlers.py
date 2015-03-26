from distutils.spawn import find_executable
from logging import getLogger
import os
from subprocess import check_output
from tempfile import TemporaryFile
from picky.requirements import Requirements

logger = getLogger(__name__)


class Handler(object):

    args = ()
    name = None

    @staticmethod
    def parse_line(line):
        raise NotImplementedError

    @staticmethod
    def serialise_line(name, version):
        raise NotImplementedError

    def __init__(self, command, path):
        self.executable = find_executable(command)
        path_exists = os.path.exists(path)

        if self.executable:
            text = check_output((command, )+self.args,
                                stderr=TemporaryFile())
            logger.info('Using %r for %s', self.executable, self.name)
        else:
            text = ''
            logger.debug('No %s found', self.name)
        self.used = self.requirements(text)

        if path_exists:
            with open(path) as source:
                text = source.read()
            logger.info('Using %r for %s', path, self.name)
        else:
            text = ''
            logger.debug('No requirements file found for %s', self.name)
        self.specified = self.requirements(text)

        if path_exists and not self.executable:
            logger.error('%r found but %s missing', path, self.name)

    def requirements(self, text):
        return Requirements(text, self.parse_line, self.serialise_line)


class PipHandler(Handler):

    name = 'pip'
    args = ('freeze', )

    @staticmethod
    def parse_line(line):
        line = line.split('#')[0]
        if '==' in line:
            return (p.strip() for p in line.split('=='))

    @staticmethod
    def serialise_line(name, version):
        return name + '==' + version


class CondaHandler(Handler):

    name = 'conda'
    args = ('list', '-e')

    @staticmethod
    def parse_line(line):
        line = line.split('#')[0]
        parts = [p.strip() for p in line.split('=')]
        if len(parts) > 1:
            return parts[:2]

    @staticmethod
    def serialise_line(name, version):
        return name + '=' + version

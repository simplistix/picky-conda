from distutils.spawn import find_executable
from logging import getLogger
import os
import re
from subprocess import Popen, PIPE

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

    def read_source(self, if_, callable_, param, source):
        if if_:
            logger.info('Using %r for %s', param, self.name)
            text = callable_(param)
        else:
            logger.debug('%r not found', param)
            text = ''

        if isinstance(text, bytes):
            text = text.decode('ascii')

        return self.requirements(text, source)

    def run_command(self, command):
        process = Popen((command, )+self.args, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        if stderr:
            if isinstance(stderr, bytes):
                stderr = stderr.decode('ascii')
            logger.error('%s gave errors: %s', self.name, stderr)
        return stdout

    def read_file(self, path):
        with open(path) as source:
            return source.read()

    def find_executable(self, command):
        executable = find_executable(command)
        if executable:
            return True, os.path.abspath(executable)
        else:
            return False, command

    def __init__(self, command, path):
        self.executable_found, executable = self.find_executable(command)
        path_exists = os.path.exists(path)
        self.path = path

        self.used = self.read_source(
            if_=self.executable_found,
            callable_=self.run_command,
            param=executable,
            source=' '.join((self.name, )+self.args)
        )

        self.specified = self.read_source(
            if_=path_exists,
            callable_=self.read_file,
            param=path,
            source=os.path.split(path)[-1]
        )

        if path_exists and not self.executable_found:
            logger.error('%r found but %s missing', path, self.name)

    def requirements(self, text, source):
        return Requirements(text,
                            self.parse_line,
                            self.serialise_line,
                            source)

    def update(self, diff, when):
        if self.executable_found:
            if diff:
                logger.warning('Updating %r', self.path)
                self.specified.apply(diff, when)
                with open(self.path, 'w') as target:
                    target.write(self.specified.serialise())
            else:
                logger.debug('No differences to apply to %r', self.path)



class PipHandler(Handler):

    name = 'pip'
    args = ('--disable-pip-version-check', 'freeze')
    pattern = re.compile('(.+?)(\[.+?\])? *={1,3}(.+)')

    @classmethod
    def parse_line(cls, line):
        line = line.split('#')[0]
        match = cls.pattern.match(line)
        if match:
            package, features, version = match.groups()
            if '-e ' not in package:
                return package.strip(), version.strip()

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

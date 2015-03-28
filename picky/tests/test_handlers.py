import os
from unittest import TestCase

from testfixtures import Comparison as C, LogCapture, OutputCapture, compare

from picky.handlers import CondaHandler, PipHandler, Handler
from picky.requirements import Requirements


class HandlerTestHelpers(object):

    class_ = Handler

    def path(self, filename):
        return os.path.join(
            os.path.dirname(__file__),
            'sample_output',
            filename
        )

    def make_handler(self, command, spec, *logging):
        command_path = self.path(command)
        spec_path = self.path(spec)
        with LogCapture() as log:
            with OutputCapture() as output:
                handler = self.class_(command_path, spec_path)
        # make sure there's no output!
        output.compare('')
        expected_logging = []
        for level, template in logging:
            expected_logging.append((
                'picky.handlers', level, template % dict(
                    command=command_path, spec=spec_path
                )))
        log.check(*expected_logging)
        return handler

    def check_requirements(self, obj, source, **expected_versions):
        compare(C(Requirements,
                  versions=expected_versions,
                  source=source,
                  strict=False),
                obj)


class PipTests(HandlerTestHelpers, TestCase):

    class_ = PipHandler

    def test_simple(self):
        handler = self.make_handler(
            'pip_freeze_simple.py', 'requirements.txt',
            ('INFO', "Using '%(command)s' for pip"),
            ('INFO', "Using '%(spec)s' for pip"),
        )
        self.assertTrue(handler.executable_found)
        self.check_requirements(handler.used,
                                'pip freeze',
                                testfixtures='4.1.2',
                                picky='0.0.dev0')
        self.check_requirements(handler.specified,
                                'requirements.txt',
                                foo='2',
                                baz='3')

    def test_command_no_path(self):
        handler = self.make_handler(
            'pip_freeze_simple.py', 'missing.txt',
            ('INFO', "Using '%(command)s' for pip"),
            ('DEBUG', "'%(spec)s' not found"),
        )
        self.assertTrue(handler.executable_found)
        self.check_requirements(handler.used,
                                'pip freeze',
                                testfixtures='4.1.2',
                                picky='0.0.dev0')
        self.check_requirements(handler.specified,
                                'missing.txt')

    def test_path_no_command(self):
        handler = self.make_handler(
            'missing.py', 'requirements.txt',
            ('DEBUG', "'%(command)s' not found"),
            ('INFO', "Using '%(spec)s' for pip"),
            ('ERROR', "'%(spec)s' found but pip missing")
        )
        self.assertFalse(handler.executable_found)

    def test_neither_path_nor_command(self):
        handler = self.make_handler(
            'missing.py', 'bad-requirements.txt',
            ('DEBUG', "'%(command)s' not found"),
            ('DEBUG', "'%(spec)s' not found"),
        )
        self.assertFalse(handler.executable_found)

    def test_no_vcs_remote(self):
        handler = self.make_handler(
            'pip_freeze_no_vcs_remote.py', 'requirements.txt',
            ('INFO', "Using '%(command)s' for pip"),
            ('INFO', "Using '%(spec)s' for pip"),
        )
        self.assertTrue(handler.executable_found)
        self.check_requirements(handler.used,
                                'pip freeze',
                                testfixtures='4.1.2',
                                picky='0.0.dev0')
        self.check_requirements(handler.specified,
                                'requirements.txt',
                                foo='2',
                                baz='3')

    def test_parse_commented(self):
        compare(None, self.class_.parse_line('# foo==1.0'))

    def test_parse_post_comment(self):
        compare(('foo', '1.0'), self.class_.parse_line(' foo == 1.0 #barrr'))

    def test_serialise(self):
        compare('foo==1.0', self.class_.serialise_line('foo', '1.0'))


class CondaTests(HandlerTestHelpers, TestCase):

    class_ = CondaHandler

    def test_simple(self):
        handler = self.make_handler(
            'conda_list_simple.py', 'conda_versions.txt',
            ('INFO', "Using '%(command)s' for conda"),
            ('INFO', "Using '%(spec)s' for conda"),
        )
        self.assertTrue(handler.executable_found)
        self.check_requirements(handler.used,
                                'conda list -e',
                                python='2.7.9',
                                pip='6.0.8')
        self.check_requirements(handler.specified,
                                'conda_versions.txt',
                                foo='2',
                                baz='3')

    def test_command_no_path(self):
        handler = self.make_handler(
            'conda_list_simple.py', 'missing.txt',
            ('INFO', "Using '%(command)s' for conda"),
            ('DEBUG', "'%(spec)s' not found"),
        )
        self.assertTrue(handler.executable_found)
        self.check_requirements(handler.used,
                                'conda list -e',
                                python='2.7.9',
                                pip='6.0.8')
        self.check_requirements(handler.specified,
                                'missing.txt')

    def test_path_no_command(self):
        handler = self.make_handler(
            'missing.py', 'conda_versions.txt',
            ('DEBUG', "'%(command)s' not found"),
            ('INFO', "Using '%(spec)s' for conda"),
            ('ERROR', "'%(spec)s' found but conda missing")
        )
        self.assertFalse(handler.executable_found)

    def test_neither_path_nor_command(self):
        handler = self.make_handler(
            'missing.py', 'bad-conda-versions.txt',
            ('DEBUG', "'%(command)s' not found"),
            ('DEBUG', "'%(spec)s' not found"),
        )
        self.assertFalse(handler.executable_found)

    def test_parse_commented(self):
        compare(None, self.class_.parse_line('# foo=1.0=1'))

    def test_parse_post_comment(self):
        compare(('foo', '1.0'), self.class_.parse_line(' foo=1.0=py27_0 #barr'))

    def test_serialise(self):
        compare('foo=1.0', self.class_.serialise_line('foo', '1.0'))

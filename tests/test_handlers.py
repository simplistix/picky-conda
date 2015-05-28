import os
from unittest import TestCase
from datetime import datetime

from testfixtures import Comparison as C, LogCapture, OutputCapture, compare, \
    TempDirectory

from picky.handlers import CondaHandler, PipHandler, Handler
from picky.requirements import Requirements, Diff
from tests import sample_output_path


class HandlerTestHelpers(object):

    class_ = Handler

    def check_logging(self, command_path, spec_path, log, *logging):
        expected_logging = []
        for level, template in logging:
            expected_logging.append((
                'picky.handlers', level, template % dict(
                    command=command_path, spec=spec_path
                )))
        log.check(*expected_logging)

    def make_handler(self, command, spec_path):
        command_path = sample_output_path(command)
        with OutputCapture() as output:
            handler = self.class_(command_path, spec_path)
        # make sure there's no output!
        output.compare('')
        return command_path, handler

    def make_and_check(self, command, spec, *logging):
        spec_path = sample_output_path(spec)
        with LogCapture() as log:
            command_path, handler = self.make_handler(command, spec_path)
        self.check_logging(command_path, spec_path, log, *logging)
        return handler

    def check_requirements(self, obj, source, **expected_versions):
        compare(C(Requirements,
                  versions=expected_versions,
                  source=source,
                  strict=False),
                obj)

    def check_update(self, command,
                     original_spec, expected_spec,
                     *logging):
        spec_name = 'spec.txt'
        with TempDirectory() as dir:
            if original_spec:
                dir.write(spec_name, original_spec)
            with LogCapture() as log:
                spec_path = dir.getpath(spec_name)
                command_path, handler = self.make_handler(
                    command, spec_path
                )
                diff = Diff(handler.specified, handler.used)
                handler.update(diff, datetime(2001, 1, 2, 3, 4, 5))
                if os.path.exists(spec_path):
                    actual_spec = dir.read(spec_name)
                else:
                    actual_spec = None
                compare(expected_spec, actual_spec)
        self.check_logging(command_path, spec_path, log, *logging)



class PipTests(HandlerTestHelpers, TestCase):

    class_ = PipHandler

    def test_simple(self):
        handler = self.make_and_check(
            'pip_freeze_simple.py', 'requirements.txt',
            ('INFO', "Using '%(command)s' for pip"),
            ('INFO', "Using '%(spec)s' for pip"),
        )
        self.assertTrue(handler.executable_found)
        self.check_requirements(handler.used,
                                'pip --disable-pip-version-check freeze',
                                testfixtures='4.1.2',
                                picky='0.0.dev0')
        self.check_requirements(handler.specified,
                                'requirements.txt',
                                foo='2',
                                baz='3')

    def test_command_no_path(self):
        handler = self.make_and_check(
            'pip_freeze_simple.py', 'missing.txt',
            ('INFO', "Using '%(command)s' for pip"),
            ('DEBUG', "'%(spec)s' not found"),
        )
        self.assertTrue(handler.executable_found)
        self.check_requirements(handler.used,
                                'pip --disable-pip-version-check freeze',
                                testfixtures='4.1.2',
                                picky='0.0.dev0')
        self.check_requirements(handler.specified,
                                'missing.txt')

    def test_path_no_command(self):
        handler = self.make_and_check(
            'missing.py', 'requirements.txt',
            ('DEBUG', "'%(command)s' not found"),
            ('INFO', "Using '%(spec)s' for pip"),
            ('ERROR', "'%(spec)s' found but pip missing")
        )
        self.assertFalse(handler.executable_found)

    def test_neither_path_nor_command(self):
        handler = self.make_and_check(
            'missing.py', 'bad-requirements.txt',
            ('DEBUG', "'%(command)s' not found"),
            ('DEBUG', "'%(spec)s' not found"),
        )
        self.assertFalse(handler.executable_found)

    def test_no_vcs_remote(self):
        handler = self.make_and_check(
            'pip_freeze_no_vcs_remote.py', 'requirements.txt',
            ('INFO', "Using '%(command)s' for pip"),
            ('ERROR', 'pip gave errors: Error when trying to get requirement '
                      'for VCS system Command "/usr/bin/git config '
                      'remote.origin.url" failed with error code 1 in xxx, '
                      'falling back to uneditable format\n'
                      'Could not determine repository location of '
                      '/Users/chris/LocalGIT/picky\n'),
            ('INFO', "Using '%(spec)s' for pip"),
        )
        self.assertTrue(handler.executable_found)
        self.check_requirements(handler.used,
                                'pip --disable-pip-version-check freeze',
                                testfixtures='4.1.2',
                                picky='0.0.dev0')
        self.check_requirements(handler.specified,
                                'requirements.txt',
                                foo='2',
                                baz='3')
        compare('## !! Could not determine repository location\n'
                'picky==0.0.dev0\n'
                'testfixtures==4.1.2\n',
                handler.used.serialise())

    def test_no_git(self):
        handler = self.make_and_check(
            'pip_freeze_no_git.py', 'x',
            ('INFO', "Using '%(command)s' for pip"),
            ('ERROR', 'pip gave errors: cannot determine version of '
                      'editable source in /Users/chris/LocalGIT/picky\n'
                      '(git command not found in path)\n'),
            ('DEBUG', "'%(spec)s' not found"),
        )
        self.assertTrue(handler.executable_found)
        self.check_requirements(handler.used,
                                'pip --disable-pip-version-check freeze')
        compare('-e picky==0.0.dev0\n', handler.used.serialise())

    def test_git(self):
        handler = self.make_and_check(
            'pip_freeze_git.py', 'x',
            ('INFO', "Using '%(command)s' for pip"),
            ('DEBUG', "'%(spec)s' not found"),
        )
        self.assertTrue(handler.executable_found)
        self.check_requirements(handler.used,
                                'pip --disable-pip-version-check freeze')
        compare('-e git+https://github.com/Simplistix/picky.git'
                '@181903dc9a100ead5879ebc0ed81d12145be68d9'
                '#egg=picky-master\n', handler.used.serialise())

    def test_parse_commented(self):
        compare(None, self.class_.parse_line('# foo==1.0'))

    def test_parse_post_comment(self):
        compare(('foo', '1.0'), self.class_.parse_line(' foo == 1.0 #barrr'))

    def test_serialise(self):
        compare('foo==1.0', self.class_.serialise_line('foo', '1.0'))

    def test_update_create(self):
        self.check_update(
            'pip_freeze_simple.py',
            # original spec:
            None,
            # expected spec:
            '# picky added the following on 2001-01-02 03:04:05:\n'
            'picky==0.0.dev0\n'
            'testfixtures==4.1.2\n',
            # expected logging:
            ('INFO', "Using '%(command)s' for pip"),
            ('DEBUG', "'%(spec)s' not found"),
            ('WARNING', "Updating '%(spec)s'")
        )

    def test_update_changes(self):
        self.check_update(
            'pip_freeze_for_update.py',
            # original spec:
            '\n'
            'c==1.0\n'
            '#a comment\n'
            'a==2\n'
            'b==3\n',
            # expected spec:
            '\n'
            'c==1.0\n'
            '#a comment\n'
            '# a==2 removed by picky on 2001-01-02 03:04:05\n'
            '# b==3 updated by picky to 4 on 2001-01-02 03:04:05\n'
            '# picky added the following on 2001-01-02 03:04:05:\n'
            'd==5\n'
            '# picky updated the following on 2001-01-02 03:04:05:\n'
            'b==4\n',
            # expected logging:
            ('INFO', "Using '%(command)s' for pip"),
            ('INFO', "Using '%(spec)s' for pip"),
            ('WARNING', "Updating '%(spec)s'")
        )

    def test_update_no_changes(self):
        requirements_content = '''
        # some comment
        picky==0.0.dev0
        # more junk
        # junk==1.2.3 removed by picky before

        testfixtures==4.1.2
'''
        self.check_update(
            'pip_freeze_simple.py',
            # original spec:
            requirements_content,
            # expected spec:
            requirements_content,
            # expected logging:
            ('INFO', "Using '%(command)s' for pip"),
            ('INFO', "Using '%(spec)s' for pip"),
            ('DEBUG', "No differences to apply to '%(spec)s'")
        )

    def test_update_no_command(self):
        self.check_update(
            'missing.py',
            # original spec:
            None,
            # expected spec:
            None,
            # expected logging:
            ('DEBUG', "'%(command)s' not found"),
            ('DEBUG', "'%(spec)s' not found"),
        )


class CondaTests(HandlerTestHelpers, TestCase):

    class_ = CondaHandler

    def test_simple(self):
        handler = self.make_and_check(
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
        handler = self.make_and_check(
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
        handler = self.make_and_check(
            'missing.py', 'conda_versions.txt',
            ('DEBUG', "'%(command)s' not found"),
            ('INFO', "Using '%(spec)s' for conda"),
            ('ERROR', "'%(spec)s' found but conda missing")
        )
        self.assertFalse(handler.executable_found)

    def test_neither_path_nor_command(self):
        handler = self.make_and_check(
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

    def test_update_create(self):
        self.check_update(
            'conda_list_simple.py',
            # original spec:
            None,
            # expected spec:
            '# picky added the following on 2001-01-02 03:04:05:\n'
            'pip=6.0.8\n'
            'python=2.7.9\n',
            # expected logging:
            ('INFO', "Using '%(command)s' for conda"),
            ('DEBUG', "'%(spec)s' not found"),
            ('WARNING', "Updating '%(spec)s'")
        )

    def test_update_changes(self):
        self.check_update(
            'conda_list_for_update.py',
            # original spec:
            '\n'
            'c=1.0=py2_1\n'
            '#a comment\n'
            'a=2=py2_2\n'
            'b=3=py2_3\n',
            # expected spec:
            '\n'
            'c=1.0=py2_1\n'
            '#a comment\n'
            '# a=2=py2_2 removed by picky on 2001-01-02 03:04:05\n'
            '# b=3=py2_3 updated by picky to 4 on 2001-01-02 03:04:05\n'
            '# picky added the following on 2001-01-02 03:04:05:\n'
            'd=5\n'
            '# picky updated the following on 2001-01-02 03:04:05:\n'
            'b=4\n',
            # expected logging:
            ('INFO', "Using '%(command)s' for conda"),
            ('INFO', "Using '%(spec)s' for conda"),
            ('WARNING', "Updating '%(spec)s'")
        )

    def test_update_no_changes(self):
        requirements_content = '''
        # we won't update just because of build number!
        python=2.7.9=12
        # more junk
        # junk==1.2.3 removed by picky before

        pip=6.0.8
'''
        self.check_update(
            'conda_list_simple.py',
            # original spec:
            requirements_content,
            # expected spec:
            requirements_content,
            # expected logging:
            ('INFO', "Using '%(command)s' for conda"),
            ('INFO', "Using '%(spec)s' for conda"),
            ('DEBUG', "No differences to apply to '%(spec)s'")
        )

    def test_update_no_command(self):
        self.check_update(
            'missing.py',
            # original spec:
            None,
            # expected spec:
            None,
            # expected logging:
            ('DEBUG', "'%(command)s' not found"),
            ('DEBUG', "'%(spec)s' not found"),
        )

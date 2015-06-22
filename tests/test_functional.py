from distutils.spawn import find_executable
import os
import re
from unittest import TestCase

from testfixtures import (
    LogCapture, OutputCapture, Replacer, ShouldRaise, compare,
    test_datetime, TempDirectory
)

from picky.main import main
from tests import sample_output_path


# a path to pre-pend to $PATH when we can't activate the conda env and want
# to run tests, such as PyCharm
binary_dir = os.environ.get('BINARY_DIR')
def search_path():
    path = os.environ.get('PATH')
    if binary_dir:
        path = binary_dir + os.pathsep + path
    return path

class TestHelpers(object):

    def setUp(self):
        self.dir = TempDirectory()
        self.missing = self.dir.getpath('missing')
        self.path = search_path()

    def tearDown(self):
        self.dir.cleanup()
        
    def run_main(self, args=(), output='', return_code=0):
        # so we don't leave log handlers lying around...
        # ...level is so that we check the log level is correctly set
        # in setup_logging
        with LogCapture(level=100):
            with Replacer() as r:
                # set argv
                argv = ['x'] + args
                r.replace('sys.argv', argv)
                r.replace('picky.main.datetime', test_datetime(2001, 1, 2, 3, 4, 5))
                # set PATH env variable
                r.replace('os.environ.PATH', self.path)
                # change to tempdir
                cwd = os.getcwd()
                try:
                    os.chdir(self.dir.path)
                    # get the exit code
                    with ShouldRaise(SystemExit) as s:
                        # capture output
                        with OutputCapture() as actual:
                            main()
                finally:
                    os.chdir(cwd)
    
        # compare output, with timestamp subbed out
        captured = re.sub('[\d\- :]{19}', '(ts)', actual.captured)
        compare(output, captured)
    
        # compare return code
        compare(return_code, s.raised.code)


class FunctionalTests(TestHelpers, TestCase):
    
    def test_requirements_no_pip(self):
        pip_requirements = self.dir.write('requirements.txt', '''
x==1
''')
        conda_requirements = self.dir.write('conda_versions.txt', '''
pip=6.0.8
python=2.7.9
''')
        self.run_main(args=['--pip', self.missing,
                            '--pip-requirements', pip_requirements,
                            '--conda', sample_output_path('conda_list_simple.py'),
                            '--conda-versions', conda_requirements],
                      output="""\
'{0}' found but pip missing
x 1 missing from pip --disable-pip-version-check freeze
""".format(pip_requirements),
                      return_code=1)

    def test_versions_no_conda(self):
        pip_requirements = self.dir.write('requirements.txt', '''
picky==0.0.dev0
testfixtures==4.1.2
''')
        conda_requirements = self.dir.write('conda-versions.txt', '''
x=1=2
''')
        self.run_main(args=['--pip', sample_output_path('pip_freeze_simple.py'),
                            '--pip-requirements', pip_requirements,
                            '--conda', self.missing,
                            '--conda-versions', conda_requirements],
                      output="""\
'{0}' found but conda missing
x 1 missing from conda list -e
""".format(conda_requirements),
                      return_code=1)

    def test_no_conda_or_pip(self):
        pip_missing = self.dir.getpath('pip')
        conda_missing = self.dir.getpath('conda')
        self.run_main(args=['--pip', pip_missing,
                            '--conda', conda_missing,
                            '--pip-requirements', self.missing,
                            '--conda-versions', self.missing],
                      output="""\
Neither {0} nor {1} could be found
""".format(pip_missing, conda_missing),
                      return_code=2)

    def test_just_pip(self):
        requirements = self.dir.write('requirements.txt', '''
picky==0.0.dev0
testfixtures==4.1.2
''')
        self.run_main(args=['--pip', sample_output_path('pip_freeze_simple.py'),
                            '--pip-requirements', requirements,
                            '--conda', self.missing,
                            '--conda-versions', self.missing],
                      output="",
                      return_code=0)

    def test_just_conda(self):
        requirements = self.dir.write('requirements.txt', '''
pip=6.0.8
python=2.7.9
''')
        self.run_main(args=['--pip', self.missing,
                            '--pip-requirements', self.missing,
                            '--conda', sample_output_path('conda_list_simple.py'),
                            '--conda-versions', requirements],
                      output="",
                      return_code=0)

    def test_pip_no_requirements(self):
        requirements = self.dir.getpath('requirements.txt')
        self.run_main(args=['--pip', sample_output_path('pip_freeze_simple.py'),
                            '--pip-requirements', requirements,
                            '--conda', self.missing,
                            '--conda-versions', self.missing],
                      output="""\
picky 0.0.dev0 missing from requirements.txt
testfixtures 4.1.2 missing from requirements.txt
""",
                      return_code=1)
        self.dir.check()

    def test_conda_no_versions(self):
        requirements = self.dir.getpath('conda-versions.txt')
        self.run_main(args=['--pip', self.missing,
                            '--conda', self.missing,
                            '--conda', sample_output_path('conda_list_simple.py'),
                            '--conda-versions', requirements],
                      output="""\
pip 6.0.8 missing from conda-versions.txt
python 2.7.9 missing from conda-versions.txt
""",
                      return_code=1)
        self.dir.check()

    def test_different(self):
        requirements_content = """
picky==0.0.dev0
somethingelse==1.0
testfixtures==5
"""
        conda_versions_content = """
gonepack=1.0
pip=6.0.8
python=3.4.0
"""
        requirements = self.dir.write('requirements.txt',
                                      requirements_content)
        conda_versions = self.dir.write('conda-versions.txt',
                                        conda_versions_content)
        self.run_main(args=['--pip', sample_output_path('pip_freeze_simple.py'),
                            '--pip-requirements', requirements,
                            '--conda', sample_output_path('conda_list_simple.py'),
                            '--conda-versions', conda_versions],
                      output="""\
testfixtures 4.1.2 in pip --disable-pip-version-check freeze but 5 in requirements.txt
somethingelse 1.0 missing from pip --disable-pip-version-check freeze
python 2.7.9 in conda list -e but 3.4.0 in conda-versions.txt
gonepack 1.0 missing from conda list -e
""",
                      return_code=1)
        # check no changes!
        compare(requirements_content, self.dir.read('requirements.txt'))
        compare(conda_versions_content, self.dir.read('conda-versions.txt'))

    def test_update(self):
        requirements = self.dir.write('requirements.txt', """
picky==0.0.dev0
somethingelse==1.0
testfixtures==5
""")
        conda_versions = self.dir.write('conda-versions.txt',"""
gonepack=1.0
pip=6.0.8
python=3.4.0
""")

        self.run_main(args=['--pip', sample_output_path('pip_freeze_simple.py'),
                            '--pip-requirements', requirements,
                            '--conda', sample_output_path('conda_list_simple.py'),
                            '--conda-versions', conda_versions,
                            '--update'],
                      output="""\
testfixtures 4.1.2 in pip --disable-pip-version-check freeze but 5 in requirements.txt
somethingelse 1.0 missing from pip --disable-pip-version-check freeze
python 2.7.9 in conda list -e but 3.4.0 in conda-versions.txt
gonepack 1.0 missing from conda list -e
Updating '{0}'
Updating '{1}'
""".format(requirements, conda_versions),
                      return_code=1)
        # check no changes!
        compare("""
picky==0.0.dev0
# somethingelse==1.0 removed by picky on 2001-01-02 03:04:05
# testfixtures==5 updated by picky to 4.1.2 on 2001-01-02 03:04:05
# picky updated the following on 2001-01-02 03:04:05:
testfixtures==4.1.2
""", self.dir.read('requirements.txt'))

        compare("""
# gonepack=1.0 removed by picky on 2001-01-02 03:04:05
pip=6.0.8
# python=3.4.0 updated by picky to 2.7.9 on 2001-01-02 03:04:05
# picky updated the following on 2001-01-02 03:04:05:
python=2.7.9
""", self.dir.read('conda-versions.txt'))

    def test_update_creates(self):
        requirements = self.dir.getpath('requirements.txt')
        conda_versions = self.dir.getpath('conda-versions.txt')
        self.run_main(args=['--pip', sample_output_path('pip_freeze_simple.py'),
                            '--pip-requirements', requirements,
                            '--conda', sample_output_path('conda_list_simple.py'),
                            '--conda-versions', conda_versions,
                            '--update'],
                      output="""\
picky 0.0.dev0 missing from requirements.txt
testfixtures 4.1.2 missing from requirements.txt
pip 6.0.8 missing from conda-versions.txt
python 2.7.9 missing from conda-versions.txt
Updating '{0}'
Updating '{1}'
""".format(requirements, conda_versions),
                      return_code=1)
        compare("""\
# picky added the following on 2001-01-02 03:04:05:
picky==0.0.dev0
testfixtures==4.1.2
""", self.dir.read('requirements.txt'))

        compare("""\
# picky added the following on 2001-01-02 03:04:05:
pip=6.0.8
python=2.7.9
""", self.dir.read('conda-versions.txt'))

    def test_combine_from_empty(self):
        requirements = self.dir.getpath('requirements.txt')
        conda_versions = self.dir.getpath('conda-versions.txt')
        self.run_main(args=['--pip', sample_output_path('pip_freeze_for_combine.py'),
                            '--pip-requirements', requirements,
                            '--conda', sample_output_path('conda_list_for_update.py'),
                            '--conda-versions', conda_versions,
                            '--update'],
                      output="""\
b 4.1 missing from requirements.txt
c 1.0 missing from conda-versions.txt
d 5 missing from conda-versions.txt
Updating '{0}'
Updating '{1}'
""".format(requirements, conda_versions),
                      return_code=1)
        compare("""\
# picky added the following on 2001-01-02 03:04:05:
b==4.1
""", self.dir.read('requirements.txt'))

        compare("""\
# picky added the following on 2001-01-02 03:04:05:
c=1.0
d=5
""", self.dir.read('conda-versions.txt'))

    def test_combine_changes_both_update(self):
        requirements = self.dir.write('requirements.txt', '''
d==5
# some other comment
b==4.1
''')
        conda_versions = self.dir.write('conda-versions.txt', '''
# This file may be used to create an environment using:
# $ conda create --name <env> --file <this file>
# platform: osx-64
d=5=1
b=4=2
c=1.0=3
''')
        self.run_main(args=['--pip', sample_output_path('pip_freeze_for_combine.py'),
                            '--pip-requirements', requirements,
                            '--conda', sample_output_path('conda_list_for_update.py'),
                            '--conda-versions', conda_versions,
                            '--update'],
                      output="""\
d 5 missing from pip --disable-pip-version-check freeze
b 4 missing from conda list -e
Updating '{0}'
Updating '{1}'
""".format(requirements, conda_versions),
                      return_code=1)
        compare("""
# d==5 removed by picky on 2001-01-02 03:04:05
# some other comment
b==4.1
""", self.dir.read('requirements.txt'))

        compare("""
# This file may be used to create an environment using:
# $ conda create --name <env> --file <this file>
# platform: osx-64
d=5=1
# b=4=2 removed by picky on 2001-01-02 03:04:05
c=1.0=3
""", self.dir.read('conda-versions.txt'))

    def test_changes_nothing(self):
        requirements_content = '''
b==4.1
'''
        conda_content = '''
c=1.0
d=5
'''
        requirements = self.dir.write('requirements.txt',
                                      requirements_content)
        conda_versions = self.dir.write('conda-versions.txt',
                                        conda_content)
        self.run_main(args=['--pip', sample_output_path('pip_freeze_for_combine.py'),
                            '--pip-requirements', requirements,
                            '--conda', sample_output_path('conda_list_for_update.py'),
                            '--conda-versions', conda_versions,
                            '--update'],
                      output="".format(requirements, conda_versions),
                      return_code=0)
        compare(requirements_content, self.dir.read('requirements.txt'))
        compare(conda_content, self.dir.read('conda-versions.txt'))

    def test_update_pip_conda_missing(self):
        requirements = self.dir.write('requirements.txt', """
picky==0.0.dev0
somethingelse==1.0
testfixtures==5
""")

        self.run_main(args=['--pip', sample_output_path('pip_freeze_simple.py'),
                            '--pip-requirements', requirements,
                            '--conda', self.missing,
                            '--conda-versions', self.missing,
                            '--update'],
                      output="""\
testfixtures 4.1.2 in pip --disable-pip-version-check freeze but 5 in requirements.txt
somethingelse 1.0 missing from pip --disable-pip-version-check freeze
Updating '{0}'
""".format(requirements),
                      return_code=1)
        # check changes written:
        compare("""
picky==0.0.dev0
# somethingelse==1.0 removed by picky on 2001-01-02 03:04:05
# testfixtures==5 updated by picky to 4.1.2 on 2001-01-02 03:04:05
# picky updated the following on 2001-01-02 03:04:05:
testfixtures==4.1.2
""", self.dir.read('requirements.txt'))
        # check no conda-versions.txt has appeared!
        self.dir.check('requirements.txt')

    def test_bad_log_level(self):
        self.run_main(args=['-l', 'wrong'],
                      output="""\
usage: x [-h] [--pip PIP] [--conda CONDA]
         [--pip-requirements PIP_REQUIREMENTS]
         [--conda-versions CONDA_VERSIONS] [--update] [-l LOG_LEVEL]
x: error: argument -l/--log-level: invalid log_level value: 'wrong'
""",
                      return_code=2)


class SelfTests(TestHelpers, TestCase):

    # use our dev environment to test everything for real

    def test_functional(self):
        # first run, should write files the files
        # we artificially up the log level so we don't see output
        # that will be unreliable to test against. (it's tested above!)
        self.run_main(args=['--update', '-l', 'ERROR'],
                      output='',
                      return_code=1)
        # now we should have two config files
        self.dir.check('conda_versions.txt', 'requirements.txt')
        # running again, even in debug, should give no unexpected
        # output
        pip = find_executable('pip', self.path)
        conda = find_executable('conda', self.path)
        self.run_main(args=['-l', 'debug'],
                      output='''\
(ts) INFO    Using '{0}' for pip
(ts) INFO    Using 'requirements.txt' for pip
(ts) INFO    Using '{1}' for conda
(ts) INFO    Using 'conda_versions.txt' for conda
'''.format(pip, conda),
                      return_code=0)

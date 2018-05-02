import pytest
from testfixtures import OutputCapture, Replacer, compare

from picky.main import main
from tests.test_env import sample_serialized


sample_serialized_no_build = """\
name: package
channels:
- defaults
- conda-forge
dependencies:
- ca-certificates=2018.03.07
- certifi=2018.1.18
- libcxx=4.0.1
- pip:
  - alabaster==0.7.10
  - attrs==17.4.0
  - urllib3==1.22
"""


def mock_conda_env_export(include_build=True):
    if include_build:
        return sample_serialized
    else:
        return sample_serialized_no_build


def run(argv, expected_output=''):
    with Replacer() as r:
        r.replace('sys.argv', ['x']+argv)
        r.replace('picky.main.conda_env_export',
                  mock_conda_env_export)
        with OutputCapture() as output:
            rc = main()
    output.compare(expected_output)
    return rc


@pytest.fixture(autouse=True)
def cwd(tmpdir):
    tmpdir.chdir()
    yield


def test_lock_simple(tmpdir):
    rc = run(['lock'])
    compare(rc, expected=None)
    compare(tmpdir.join('environment.lock.yaml').read(),
            expected=sample_serialized)

sample_config = """
ignore:
  - attrs
  - libcxx
develop:
  mypackage: .
detail: version
"""

serialized_after_config = """\
name: package
channels:
- defaults
- conda-forge
dependencies:
- ca-certificates=2018.03.07
- certifi=2018.1.18
- pip:
  - alabaster==0.7.10
  - urllib3==1.22
  - -e .
"""


def test_lock_with_config(tmpdir):
    tmpdir.join('picky.yaml').write(sample_config)
    rc = run(['lock'])
    compare(rc, expected=None)
    compare(tmpdir.join('environment.lock.yaml').read(),
            expected=serialized_after_config)


def test_check_okay(tmpdir):
    p = tmpdir.join('environment.yaml')
    p.write(sample_serialized)
    rc = run(['--concrete', str(p), 'check'])
    compare(rc, expected=0)


not_okay_output = """
Expected environment does not match actual:
--- expected
+++ actual
@@ -1,3 +1,13 @@
-channels: []
-dependencies: []
+channels:
+- conda-forge
+- defaults
+dependencies:
+- ca-certificates=2018.03.07=0
+- certifi=2018.1.18=py36_0
+- libcxx=4.0.1=h579ed51_0
+- pip:
+  - alabaster==0.7.10
+  - attrs==17.4.0
+  - urllib3==1.22
+  - -e .
"""


def test_check_not_okay(tmpdir):
    p = tmpdir.join('environment.lock.yaml')
    p.write('')
    rc = run(['check'], expected_output=not_okay_output)
    compare(rc, expected=1)

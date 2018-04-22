import os

import pytest
from testfixtures import compare

from picky.conda import conda_env_export
from picky.env import Environment


class TestRunCommand(object):

    @pytest.fixture(autouse=True)
    def has_conda_env(self):
        # these tests must be run from within an activated conda env:
        assert 'CONDA_DEFAULT_ENV' in os.environ

    def test_structure(self):
        env = Environment.from_string(conda_env_export())
        compare(env.keys(),
                expected=['name', 'channels', 'conda', 'pip', 'develop'])

    def test_build(self):
        env = Environment.from_string(conda_env_export(include_build=True))
        assert isinstance(env['conda']['python'].build, str)

    def test_no_build(self):
        env = Environment.from_string(conda_env_export(include_build=False))
        assert env['conda']['python'].build is None

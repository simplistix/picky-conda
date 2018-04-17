import os
from subprocess import check_output


def conda_env_export(include_build=True):
    conda = os.environ.get('CONDA_EXE', 'conda')
    cmd = [conda, 'env', 'export']
    if not include_build:
        cmd.append('--no-builds')
    return check_output(cmd)

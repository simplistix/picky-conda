#!/usr/bin/env python
import sys

if sys.argv[1:] != ['list', '-e']:
    raise TypeError(repr(sys.argv))

sys.stdout.write('''\
# This file may be used to create an environment using:
# $ conda create --name <env> --file <this file>
# platform: osx-64
pip=6.0.8=py27_0
python=2.7.9=1
''')

sys.exit(0)
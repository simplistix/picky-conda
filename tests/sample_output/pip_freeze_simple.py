#!/usr/bin/env python
import sys

if sys.argv[1:] != ['--disable-pip-version-check', 'freeze']:
    raise TypeError(repr(sys.argv))

sys.stdout.write('''\
picky==0.0.dev0
testfixtures==4.1.2
''')

sys.exit(0)
#!/usr/bin/env python
import sys

if sys.argv[1:] == ['freeze']:
    sys.stdout.write('''\
    picky==0.0.dev0
    testfixtures==4.1.2
    ''')
    sys.exit(0)
elif sys.argv[1:] == ['--disable-pip-version-check', '--version']:
    sys.stderr.write('''\
Usage:
  pip <command> [options]

no such option: --disable-pip-version-check
''')
    sys.exit(2)
else:
    raise TypeError(repr(sys.argv))


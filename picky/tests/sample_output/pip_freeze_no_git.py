#!/usr/bin/env python
import sys

sys.stderr.write('''\
cannot determine version of editable source in /Users/chris/LocalGIT/picky
(git command not found in path)
''')

sys.stdout.write('''\
-e picky==0.0.dev0
''')

sys.exit(0)
#!/usr/bin/env python
import sys

sys.stderr.write('''\
Error when trying to get requirement for VCS system Command "/usr/bin/git config remote.origin.url" failed with error code 1 in xxx, falling back to uneditable format
Could not determine repository location of /Users/chris/LocalGIT/picky
''')

sys.stdout.write('''\
## !! Could not determine repository location
picky==0.0.dev0
testfixtures==4.1.2
''')

sys.exit(0)
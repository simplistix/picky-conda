from unittest import TestCase
from datetime import datetime
from testfixtures import compare
from picky.requirements import Requirements, Diff


def parse_line(line):
    if '=' in line:
        return (part.strip() for part in line.split('='))


def serialise_line(name, version):
    return name+'='+version


def requirements(text):
    return Requirements(text, parse_line, serialise_line)


class AbstractTests(TestCase):

    def test_idempotent(self):
        text = '''
# hello
x=1
y=2
'''
        r = requirements(text)
        compare(r.serialise(), text)

    def test_diff(self):
        r1 = requirements('''
p1=1
p2=2
p3=3
        ''')
        r2 = requirements('''
p2=2
p3=3.1
p4=4
        ''')
        actual = Diff(r1, r2)

        compare(actual.added, dict(p4='4'))
        compare(actual.removed, dict(p1='1'))
        compare(actual.changed, dict(p3='3.1'))

        self.assertTrue(actual)

    def test_same(self):
        r = requirements('''
p1=1
        ''')
        actual = Diff(r, r)

        compare(actual.added, dict())
        compare(actual.removed, dict())
        compare(actual.changed, dict())

        self.assertFalse(actual)

    def test_update(self):
        r1 = requirements('''
p1=1
p2=2
p3=3
''')
        r2 = requirements('''
p2=2
p3=3.1
p4=4
        ''')
        diff = Diff(r1, r2)
        r1.apply(diff, datetime(2001, 2, 3, 4, 5, 6))

        compare(r1.serialise(), '''
# p1=1 removed by picky on 2001-02-03 04:05:06
p2=2
# p3=3 updated by picky to 3.1 on 2001-02-03 04:05:06
# picky changes from 2001-02-03 04:05:06 below:
p4=4
p3=3.1
''')

    def test_combine_with(self):
        r1 = requirements('''
p1=1
p2=2
p3=3
''')
        r2 = requirements('''
p2=2
p3=3.1
p4=4
''')

        r1.combine_with(r2, datetime(2001, 2, 3, 4, 5, 6))

        compare(r1.serialise(), '''
p1=1
p2=2
# p3=3 removed by picky on 2001-02-03 04:05:06
''')

        compare(r2.serialise(), '''
# p2=2 removed by picky on 2001-02-03 04:05:06
p3=3.1
p4=4
''')



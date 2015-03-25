class Diff(object):

    def __init__(self, x, y):
        self.added = {}
        self.removed = {}
        self.changed = {}

        x_packages = set(x.versions)
        y_packages = set(y.versions)

        for package in y_packages - x_packages:
            self.added[package] = y.versions[package]

        for package in x_packages - y_packages:
            self.removed[package] = x.versions[package]

        for package in x_packages & y_packages:
            x_version = x.versions[package]
            y_version = y.versions[package]
            if x_version != y_version:
                self.changed[package] = y_version


class Requirements(object):

    def __init__(self, text, parse_line, serialise_line):
        self.serialise_line = serialise_line
        self.lines = []
        self.versions = {}
        self.map = {}
        for i, line in enumerate(text.splitlines()):
            self.lines.append(line)
            parsed = parse_line(line)
            if parsed:
                name, version = parsed
                self.map[name] = i
                self.versions[name] = version

    def serialise(self):
        return '\n'.join(self.lines)+'\n'

    def comment_line(self, package, message):
        i = self.map[package]
        original = self.lines[i]
        self.lines[i] = '# {} {}'.format(original, message)

    def add_line(self, package, version):
        self.lines.append(self.serialise_line(package, version))
        self.map[package] = len(self.lines)

    def remove_line(self, package, when_str):
        self.comment_line(package, 'removed by picky on {}'.format(
            when_str
        ))
        del self.map[package]

    def when_str(self, when):
        when_str = when.strftime('%Y-%m-%d %H:%M:%S')
        return when_str

    def apply(self, diff, when):
        when_str = self.when_str(when)

        if diff.added or diff.changed:
            self.lines.append('# picky changes from {} below:'.format(when_str))

        for package, version in diff.added.items():
            self.add_line(package, version)

        for package, version in diff.changed.items():
            self.comment_line(package, 'updated by picky to {} on {}'.format(
                version, when_str
            ))
            self.add_line(package, version)

        for package in diff.removed:
            self.remove_line(package, when_str)

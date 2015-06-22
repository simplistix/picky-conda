from logging import getLogger


logger = getLogger(__name__)

class Diff(object):

    def __init__(self, x, y):
        self.added = {}
        self.removed = {}
        self.changed = {}
        self.x_source = x.source
        self.y_source = y.source

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
                self.changed[package] = x_version, y_version

    def __len__(self):
        return len(self.added) + len(self.removed) + len(self.changed)

    def log(self):
        log = logger.warn
        for package, version in sorted(self.added.items()):
            log('%s %s missing from %s', package, version, self.x_source)
        for package, versions in sorted(self.changed.items()):
            old_version, new_version = versions
            log('%s %s in %s but %s in %s',
                package, new_version, self.y_source, old_version, self.x_source)
        for package, version in sorted(self.removed.items()):
            log('%s %s missing from %s', package, version, self.y_source)


class Requirements(object):

    def __init__(self, text, parse_line, serialise_line, source):
        self.serialise_line = serialise_line
        self.source = source
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
        self.lines[i] = '# {0} {1}'.format(original, message)
        del self.map[package]
        del self.versions[package]

    def add_line(self, package, version):
        self.lines.append(self.serialise_line(package, version))
        self.map[package] = len(self.lines)
        self.versions[package] = version

    def remove_line(self, package, when_str):
        self.comment_line(package, 'removed by picky on {0}'.format(
            when_str
        ))

    @staticmethod
    def when_str(when):
        when_str = when.strftime('%Y-%m-%d %H:%M:%S')
        return when_str

    def apply(self, diff, when):
        when_str = self.when_str(when)

        if diff.added:
            self.lines.append('# picky added the following on {0}:'.format(
                when_str
            ))
            for package, version in sorted(diff.added.items()):
                self.add_line(package, version)

        if diff.changed:

            self.lines.append('# picky updated the following on {0}:'.format(
                when_str
            ))
            for package, versions in sorted(diff.changed.items()):
                old_version, new_version = versions
                self.comment_line(
                    package, 'updated by picky to {0} on {1}'.format(
                    new_version, when_str
                ))
                self.add_line(package, new_version)

        for package in diff.removed:
            self.remove_line(package, when_str)

    def combine_with(self, other, when):

        when_str = self.when_str(when)
        self_packages = set(self.versions)
        other_packages = set(other.versions)

        for package in self_packages & other_packages:
            self_version = self.versions[package]
            other_version = other.versions[package]
            if self_version == other_version:
                other.remove_line(package, when_str)
            else:
                self.remove_line(package, when_str)

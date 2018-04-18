from testfixtures import compare

from picky.config import parse_config, VERSION, BUILD


def test_not_present(tmpdir):
    config = parse_config(str(tmpdir.join('picky.yaml')))
    compare(config.ignore, expected=set(), strict=True)
    compare(config.develop, expected={})
    compare(config.detail, expected=BUILD)


def test_minimal(tmpdir):
    p = tmpdir.join('picky.yaml')
    p.write('detail: version\n')
    config = parse_config(str(p))
    compare(set(), expected=set(), strict=True)
    compare(config.develop, expected={})
    compare(config.detail, expected=VERSION)


sample_config = """
ignore:
  # mac-only:
  - appnope
develop:
  mypackage: .
detail: version
"""


def test_maximal(tmpdir):
    p = tmpdir.join('picky.yaml')
    p.write(sample_config)
    config = parse_config(str(p))
    compare(config.ignore, expected={'appnope'}, strict=True)
    compare(config.develop, expected={'mypackage': '.'})
    compare(config.detail, expected=VERSION)

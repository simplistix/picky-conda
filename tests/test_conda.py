from testfixtures import compare

from picky.conda import parse, Environment, PackageSpec

sample_export = """
name: package
channels:
  - defaults
  - conda-forge
dependencies:
  - ca-certificates=2018.03.07=0
  - certifi=2018.1.18=py36_0
  - libcxx=4.0.1=h579ed51_0
  - pip:
    - alabaster==0.7.10
    - attrs==17.4.0
    - urllib3==1.22
prefix: /Users/chris/anaconda2/envs/picky-conda
"""


class TestParsing(object):

    def test_from_string(self):
        compare(parse(sample_export),
                strict=True,
                expected=Environment({
                    'name': 'package',
                    'channels': ['defaults', 'conda-forge'],
                    'conda': [
                        PackageSpec('ca-certificates', '2018.03.07', '0'),
                        PackageSpec('certifi', '2018.1.18', 'py36_0'),
                        PackageSpec('libcxx', '4.0.1', 'h579ed51_0'),
                    ],
                    'pip': [
                        PackageSpec('alabaster', '0.7.10', None),
                        PackageSpec('attrs', '17.4.0', None),
                        PackageSpec('urllib3', '1.22', None),
                    ],
                }))

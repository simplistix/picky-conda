Changes
=======

2.0.2 (2 May 2018)
------------------

- Channel ordering is now ignored ignored by ``picky check``.

2.0.1 (22 April 2018)
---------------------

- Fix bugs in handling of packages installed in `develop` mode.

2.0.0 (20 April 2018)
-------------------

- Re-write to target just conda environments and based on `environment.yaml`,
  `environment.lock.yaml` and `picky.yaml`.

0.9.2 (1 July 2015)
-------------------

- check to see if ``pip`` takes ``--disable-pip-version-check`` before using it.


0.9.1 (23 June 2015)
--------------------

- correct the dependency specification of :mod:`argparse` so it only
  occurs on Python 2.6

0.9 (22 June 2015)
------------------

- Python 3 support

- Fixed handling of package 'extras' in pip output and specifications.

- Fixed handling of arbitrary equality clauses in pip output and specifications.

0.8 (22 June 2015)
------------------

- Initial Release

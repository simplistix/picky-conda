Usage
=====

Picky has three main uses cases:

- creating requirements files from an existing environment::

    $ picky --update
    Babel 1.3 missing from requirements.txt
    python 2.7.9 missing from conda_versions.txt
    Updating 'requirements.txt'
    Updating 'conda_versions.txt'

- ensuring the requirements completely match the packages installed::

    $ picky
    testfixtures 4.1.2 in pip freeze but 4.1.0 in requirements.txt
    Babel 1.3 missing from pip freeze
    python 2.7.9 in conda list -e but 3.4.0 in conda-versions.txt
    readline 6.2 missing from conda list -e

- updating the specifications based on the current environment::

    $ picky --update
    testfixtures 4.1.2 in pip freeze but 4.1.0 in requirements.txt
    Babel 1.3 missing from pip freeze
    python 2.7.9 in conda list -e but 3.4.0 in conda-versions.txt
    readline 6.2 missing from conda list -e
    Updating 'requirements.txt'
    Updating 'conda_versions.txt'

Return codes
------------

The return code set by ``picky`` will be non-zero if the requirements
files do not exactly match the packages found in the environment::

  $ picky
  Babel 1.3 missing from requirements.txt
  python 2.7.9 missing from conda_versions.txt
  $ echo $?
  1

This can be useful in continuous integration environments to check that all
packages used in your environment are specified and pinned to specific versions
by your requirements files.

Log levels
----------

If you want more information about what ``picky`` is doing, run it with a lower
log level, such as ``debug``::

  $ picky -l debug
  2015-05-01 09:08:10 INFO    Using '/path/to/pip' for pip
  2015-05-01 09:08:10 INFO    Using 'requirements.txt' for pip
  2015-05-01 09:08:10 INFO    Using '/path/to/conda' for conda
  2015-05-01 09:08:10 INFO    Using 'conda_versions.txt' for conda

Using with Pip
---------------

By default, ``picky`` will look for the ``pip`` binary on the current ``$PATH``
and will look for the requirements in a file called ``requirements.txt`` in
the current working directory.

Both the location of the pip binary and the requirements file can be specified
explicitly by using the ``--pip`` and ``--pip-requirements`` options,
respectively.

Using with Conda
----------------

By default, ``picky`` will look for the ``conda`` binary on the current ``$PATH``
and will look for the requirements in a file called ``conda_versions.txt`` in
the current working directory.

Both the location of the pip binary and the requirements file can be specified
explicitly by using the ``--conda`` and ``--conda-versions`` options,
respectively.

A new conda environment can be created from a ``conda_versions.txt`` file as
follows::

  conda create -n <environment name> --file conda_versions.txt

.. note::

  Build numbers, the third section of a conda version specifier, are ignored
  by ``picky`` as these may differ across platforms even though the package
  version is otherwise identical.

Using with Conda and Pip
------------------------

When used in a conda environment that also has some packages installed with pip,
picky will ensure that both the conda and pip requirements files do not
conflict with each other, and that a package will only appear in one or
other of the requirements files.


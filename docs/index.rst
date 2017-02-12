Picky documentation
===================

.. warning::

  This projects is currently awaiting development, do not use yet!

Picky is a tool for making sure that the packages you have installed
with `pip`__ or `conda`__ match those you have specified.

__ https://pip.pypa.io/en/stable/

__ http://conda.pydata.org/docs/

Both pip and conda have a notion of a file containing the package specifications
for an environment. For pip, the name ``requirements.txt`` is used; conda doesn't
appear to have a standard name yet, so picky defaults to using
``conda_versions.txt``.

Regardless of the name, problems can arise when the specification in those files
is either incorrect or incomplete, resulting in unexpected packages or versions
of packages being used across development, testing and production environments.

Picky provides a quick check that can be used as part of a continuous
integration pipeline to ensure that all packages in an environment are
as specified::

    $ picky
    testfixtures 4.1.2 in pip freeze but 4.1.0 in requirements.txt
    Babel 1.3 missing from pip freeze
    python 2.7.9 in conda list -e but 3.4.0 in conda-versions.txt
    readline 6.2 missing from conda list -e

If the specifications don't match the environment, the return code is set,
which will hopefully cause a continuous integration job to fail::

  $ echo $?
  1

Picky can also be used to update an existing set of specifications::

    $ picky --update
    testfixtures 4.1.2 in pip freeze but 4.1.0 in requirements.txt
    Babel 1.3 missing from pip freeze
    python 2.7.9 in conda list -e but 3.4.0 in conda-versions.txt
    readline 6.2 missing from conda list -e
    Updating 'requirements.txt'
    Updating 'conda_versions.txt'

.. toctree::
   :maxdepth: 2

   installation.rst
   use.rst
   development.rst
   changes.rst
   license.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


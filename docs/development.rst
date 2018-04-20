Development
===========

.. highlight:: bash

If you wish to contribute to this project, then you should fork the
repository found here:

https://github.com/Simplistix/picky-conda/

Once that has been done, you can follow these
instructions to perform various development tasks:

Setting up the environment
--------------------------

All development requires that you have a `conda`__ environment set up, this
can be created by doing the following from within a checkout of the above
repository, assuming you have installed conda by following its instructions::

  $ conda env create -n picky-conda python=3.6 --file environment.yaml
  $ conda activate picky-conda

__ https://pip.pypa.io/en/stable/

Running the tests
-----------------

Once you have set up and activated your conda environment, the tests can be run
from the root of your checkout as follows::

  $ pytest

Building the documentation
--------------------------

The Sphinx documentation is built by doing the following from the
directory containing setup.py::

  $ cd docs
  $ make html

Making a release
----------------

To make a release, just update the version in ``setup.py``,
update the change log, tag it
and push to https://github.com/Simplistix/picky-conda/
and Travis CI should take care of the rest.

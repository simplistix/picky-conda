Development
===========

.. highlight:: bash

If you wish to contribute to this project, then you should fork the
repository found here:

https://github.com/Simplistix/picky/

Once that has been done, you can follow these
instructions to perform various development tasks:

Setting up the environment
--------------------------

All development requires that you have a `conda`__ environment set up, this
can be created by doing the following from within a checkout of the above
repository, assuming you have installed conda by following its instructions::

  $ conda create -n picky --file=conda_versions.txt
  $ source activate picky
  (picky) $ pip install -e .

__ https://pip.pypa.io/en/stable/

Running the tests
-----------------

Once you have set up and activated your conda environment, the tests can be run
from the root of your checkout as follows::

  $ nosetests

Building the documentation
--------------------------

The Sphinx documentation is built by doing the following from the
directory containing setup.py::

  $ cd docs
  $ make html

To check that the description that will be used on PyPI renders properly,
do the following::

  $ python setup.py --long-description | rst2html.py > desc.html

The resulting ``desc.html`` should be checked by opening in a browser.

Making a release
----------------

The following should be done with your conda environment activated and will
build the distribution, upload it to PyPI and register
the metadata with PyPI::

  $ pip install -e .
  $ python setup.py sdist bdist_wheel
  $ twine upload dist/picky-<version>*

Running pip again will make sure the correct package information is
used.

This should all be done on a unix box so that a `.tgz` source
distribution is produced.

Once the above is done, make sure to go to
https://readthedocs.org/projects/picky/versions/
and make sure the new release is marked as an Active Version.

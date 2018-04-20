Picky for Conda documentation
=============================

Picky is a tool for making sure that the packages you have installed
in a `conda`__ environment match those you have specified.

__ http://conda.pydata.org/docs/

The recommended workflow is to have an `environment.yaml` that contains your abstract
requirements and an `environment.lock.yaml` that contains your concrete requirements.

An abstract set of requirements contains the minimal amount of information to install all
the packages your projects needs and any maximum or minimum version requirements there may be.
For example::

   channels:
     - conda-forge
     - defaults
   dependencies:
     - python=3
     - pandas < 0.19
     - pip:
       - testfixtures >= 6.0.0

Concrete requirements contain all the detail needed to exactly reproduce the current environment.
Given the abstract requirements above, concrete requirements would look something like::

   name: myproject
   channels:
     - conda-forge
     - defaults
   dependencies:
     - appnope=0.1.0=py27hb466136_0
     - numpy=1.11.3=py27h8a80b8c_4
     - pandas=0.18.1=np111py27_0
     ...
     - pip:
       - testfixtures==6.0.1


So, the rough workflow of a project starting from scratch would be:

1. ``conda create -n yourproject -c simplistix python=X.Y picky-conda``

2. Add abstract dependencies, including your major Python version and picky-conda, along with any
   packages that need to be installed with pip, to `environment.yaml`. After each modification of
   `environment.yaml`, run ``conda env update`` as follows::

     $ conda env update --file environment.yaml

   If you use ``conda install`` or ``pip install`` to install packages, you will need to remember
   to add those packages to your `environment.yaml` afterwards.

3. When you want to release to production or share your environment with other developers,
   lock your current exact dependencies with::

     $ picky lock

   The resultant `environment.lock.yaml` should be version controlled.

4. When setting up the environment elsewhere, the concrete requirements should be used::

     $ conda env create --force --file environment.lock.yaml

   If this is as part of an automated testing process, you should also do the following once the
   environment is set up to make sure there are no unpinned dependencies::

     $ picky check

Configuring Picky
~~~~~~~~~~~~~~~~~

Picky can be configured by placing a file called `picky.yaml` in the same directory as your
`environment.yaml`. Example content could be::

   detail: version
   develop:
     mypackage: .
   ignore:
     # mac-only:
     - appnope

Each of the sections is optional and explained below.

Lock Detail Level
-----------------

The `build` part of a conda version is the bit after the second `=` and is specific to the target
operating system. If your `environment.lock.yaml` will be used on multiple operating systems,
you can exclude the build part of versions by placing ``detail: version`` in your `picky.yaml`.

If this is done, your concrete requirements will end up looking like the following::

   name: myproject
   channels:
     - conda-forge
     - defaults
   dependencies:
     - appnope=0.1.0
     - numpy=1.11.3
     - pandas=0.18.1
     ...
     - pip:
       - testfixtures==6.0.1

Ignoring Packages
-----------------

Some packages are only installed on a particular operating system. ``conda env`` does not
currently support operating-specific dependencies. To work around this, you can include package
names in the `ignore` section of `picky.yaml` and they will not be included in any generated
`environment.lock.yaml`.

If the sample `picky.yaml` was used, then the resultant concrete requirements produced by
``picky lock`` would be::

   name: myproject
   channels:
     - conda-forge
     - defaults
   dependencies:
     - numpy=1.11.3
     - pandas=0.18.1
     ...
     - pip:
       - testfixtures==6.0.1

Note the absence of the ``appnope`` package.

Installing Packages with pip in Development Mode
------------------------------------------------

It's often handy to install an application's source using ``pip install -e`` in order to get
python packages importable and console scripts set up. However, ``conda env export`` currently
reports packages installed in this way incorrectly.

To help with all this, you can include a mapping of packages to be installed in this way to their
paths on disk in `picky.yaml` and will use that to create appropriate entries in your
`environment.lock.yaml`.

If the sample `picky.yaml` was used, then the resultant concrete requirements produced by
``picky lock`` would be::

   name: myproject
   channels:
     - conda-forge
     - defaults
   dependencies:
     - numpy=1.11.3
     - pandas=0.18.1
     ...
     - pip:
       - testfixtures==6.0.1
       - "-e ."

Further Documentation
~~~~~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 2

   installation.rst
   development.rst
   changes.rst
   license.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


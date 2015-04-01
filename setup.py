# See license.txt for license details.
# Copyright (c) 2015 Simplistix Ltd

import os, sys

from setuptools import setup, find_packages

base_dir = os.path.dirname(__file__)

setup(
    name='picky',
    version='0.0.dev0',
    author='Chris Withers',
    author_email='chris@simplistix.co.uk',
    license='MIT',
    description=(
        "A tool for checking versions of packages used by conda or pip "
        "are as specified in their requirements files."
    ),
    # long_description=open(os.path.join(base_dir,'docs','description.txt')).read(),
    url='https://github.com/Simplistix/picky',
    classifiers=[
        # 'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    extras_require=dict(
        test=[
            'testfixtures',
            'nose',
            'nose_fixes',
            'nose-cov',
            'mock',
            'manuel',
            ],
        build=['sphinx', 'pkginfo', 'setuptools-git']
    ),
    entry_points = {
        'console_scripts': [
            'picky = picky.main:main',
    ]}
)

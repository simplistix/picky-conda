import os

from setuptools import setup, find_packages

base_dir = os.path.dirname(__file__)

description = "A tool for locking down your conda package usage."

setup(
    name='picky-conda',
    version='2.0.0dev11',
    author='Chris Withers',
    author_email='chris@withers.org',
    license='MIT',
    description=description,
    long_description=description,
    url='https://github.com/Simplistix/picky-conda',
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    include_package_data=True,
    install_requires=['PyYAML'],
    entry_points = {
        'console_scripts': [
            'picky = picky.main:main',
    ]}
)

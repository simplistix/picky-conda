import os, sys

from setuptools import setup, find_packages

base_dir = os.path.dirname(__file__)

setup(
    name='picky-conda',
    version='2.0.0dev',
    author='Chris Withers',
    author_email='chris@simplistix.co.uk',
    license='MIT',
    description=(
        "A tool for checking versions of packages used by conda or pip "
        "are as specified in their requirements files."
    ),
    long_description=open(os.path.join(base_dir,'docs','description.rst')).read(),
    url='https://github.com/Simplistix/picky-conda',
    classifiers=[
        # 'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    extras_require={
        'test': [
            'testfixtures',
            'nose',
            'nose_fixes',
            'coveralls',
            ],
        'build': ['sphinx', 'pkginfo', 'setuptools-git', 'twine', 'wheel']
},
    entry_points = {
        'console_scripts': [
            'picky = picky.main:main',
    ]}
)

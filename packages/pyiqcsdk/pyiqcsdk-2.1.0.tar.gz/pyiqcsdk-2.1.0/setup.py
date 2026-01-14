#!/usr/bin/env python
from __future__ import print_function

import codecs
import os
import sys

from setuptools import setup, find_packages
from setuptools import Extension

ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)


extras_require = {
}

if sys.platform == 'win32':
    libraries = ['ws2_32']
else: # POSIX
    libraries = []

extension = Extension("tlv", ["pyiqcsdk/lib/src/tlvpacket.cpp",
                                "pyiqcsdk/lib/src/subscriberTlvWrapper.cpp",
                                "pyiqcsdk/lib/src/cipaddr.cpp",
                                "pyiqcsdk/lib/src/cmacaddr.cpp",
                                "pyiqcsdk/lib/src/addrchk.c"],
        include_dirs=["pyiqcsdk/lib/include"],
        libraries = libraries, 
        )

test_requirements = ["coverage", "flake8", "pytest"]

version = None
exec(open('pyiqcsdk/version.py').read())

long_description = ''
with open('./README.md') as readme_md:
    long_description = readme_md.read()


setup(
    name="pyiqcsdk",
    version=version,
    description="A Python SDK library for ExtremeCloud IQ Controller",
    long_description_content_type='text/markdown',
    long_description=long_description,
    author="Extreme Networks",
    author_email="pylist@extremenetworks.com",
    url='https://github.com/extremenetworks/pyxccsdk',
    project_urls={
        'Documentation': 'https://github.com/extremenetworks/pyxccsdk'
    },
    packages=find_packages(exclude=["tests", "openapi"]),
    install_requires=["requests"],
    tests_require=test_requirements,
    extras_require=extras_require,
    ext_modules=[extension],
    package_dir={'pyiqcsdk':'pyiqcsdk'},
    package_data={'pyiqcsdk':['lib/include/*.h']},
    python_requires='>=3.5',
    test_suite='tests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
    ]
)

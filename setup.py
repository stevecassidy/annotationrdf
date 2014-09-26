#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='annotationrdf',
    version='0.1.0',
    description='Annotation RDF converts various kinds of linguistic annotations to the DADA RDF format.',
    long_description=readme + '\n\n' + history,
    author='Steve Cassidy',
    author_email='steve.cassidy@mq.edu.au',
    url='https://github.com/stevecassidy/annotationrdf',
    packages=[
        'annotationrdf',
    ],
    package_dir={'annotationrdf':
                 'annotationrdf'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='annotationrdf',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
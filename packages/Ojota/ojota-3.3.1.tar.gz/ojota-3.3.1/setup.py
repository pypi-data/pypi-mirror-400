#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='Ojota',
    version='3.3.1',
    author='Luis Andres Giordano',
    author_email='agiordano@msa.com.ar',
    packages=['ojota'],
    scripts=[],
    url='http://pypi.python.org/pypi/Ojota/',
    license='LICENSE.txt',
    description='Flat File Database with ORM',
    long_description=open('README.rst').read(),
    install_requires=['six'],
)

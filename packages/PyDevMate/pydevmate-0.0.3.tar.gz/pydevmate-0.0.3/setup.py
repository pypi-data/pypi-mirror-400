#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='PyDevMate',
    version='0.0.3',                   
    author='LounisBou',                
    author_email='lounis.bou@gmail.com',  
    description='A library of utilities for python.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/lounisbou/PyDevMate',  
    license='MIT',                      
    packages=find_packages(),
    install_requires=[
        'diskcache',
        'psutil',
        'redis',
        'setuptools',
        'termcolor',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'chibi_browser>=0.1.1', 'chibi_elasticsearch>=1.2.0', 'chibi_django>=0.5.1' ]

setup(
    author="dem4ply",
    author_email='dem4ply@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Scrapper for bids online",
    entry_points={
        'console_scripts': [
            'bid_stalker=bid_stalker.cli:main',
        ],
    },
    install_requires=requirements,
    license="WTFPL",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='bid_stalker',
    name='bid_stalker',
    packages=find_packages(include=['bid_stalker', 'bid_stalker.*']),
    url='https://github.com/dem4ply/bid_stalker',
    version='0.0.1',
    zip_safe=False,
)

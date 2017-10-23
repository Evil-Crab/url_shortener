#!/usr/bin/python3

from setuptools import setup, find_packages

setup(
    name='url_shortener',
    version='0.2',

    author='Artem Nikolenko',
    author_email='a.p.nikolenko@gmail.com',
    description='Simple URL shortener',

    packages=find_packages(),

    install_requires=[
        'redis',
        'tornado',
        'validators',
    ],
    python_requires='>=3.6',

    entry_points={'console_scripts': ['url_shortener=url_shortener.app:main',
                                      ],
                  },
)

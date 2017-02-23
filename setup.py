# -*- coding: utf-8 -*-

import os
import os.path
import sys

from setuptools import find_packages
from setuptools import setup

name = 'telegram_poster_bot'
version = '0.0.1'


def find_requires():
    if sys.version_info[0] == 2:
        deps = "requirements.txt"
    elif sys.version_info[0] == 3:
        deps = "requirements3.txt"

    dir_path = os.path.dirname(os.path.realpath(__file__))
    requirements = []
    with open('{0}/{1}'.format(dir_path, deps), 'r') as reqs:
        requirements = reqs.readlines()
    return requirements


if __name__ == "__main__":
    setup(
        name=name,
        version=version,
        description='Telegram poster bot',
        long_description="""Telegram poster bot""",
        classifiers=[
            "Development Status :: 4 - Beta",
            "Programming Language :: Python"
        ],
        packages=find_packages(),
        install_requires=find_requires(),
        data_files=[('telegram_poster_bot', ['telegram_poster_bot/config.yaml'])],
        include_package_data=True,
        entry_points={
            'console_scripts': [
                'telegram_poster = telegram_poster_bot.cli:main'
            ],
        },
    )


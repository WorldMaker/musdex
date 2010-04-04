#!/usr/bin/python
from distutils.core import setup

setup(
    name='musdex',
    version='10.04.04',
    description='musdex -- VCS-aware zip archive tool',
    author='Max Battcher',
    author_email='me@worldmaker.net',
    url='http://musdex.code.worldmaker.net',
    packages=['musdex'],
    scripts=['scripts/musdex', 'scripts/xedsum'],
    requires=[
        'argparse',
        'yaml',
    ],
    license='Microsoft Reciprocal License (Ms-RL)',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development :: Version Control',
    ],
)

# vim: ai et ts=4 sts=4 sw=4

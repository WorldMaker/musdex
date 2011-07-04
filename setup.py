#!/usr/bin/python
from setuptools import setup

setup(
    name='musdex',
    version='11.07.04',
    description='musdex -- VCS-aware zip archive tool',
    author='Max Battcher',
    author_email='me@worldmaker.net',
    url='http://musdex.code.worldmaker.net',
    packages=['musdex'],
    #scripts=['scripts/musdex', 'scripts/xedsum'],
    entry_points={
        'console_scripts': [
            'musdex = musdex.__main__:main',
            'xedsum = musdex.__main__:xedsum',
        ]
    },
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
    zip_safe=True,
)

# vim: ai et ts=4 sts=4 sw=4

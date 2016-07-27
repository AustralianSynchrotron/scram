# $File: //ASP/opa/mac/scram/trunk/setup.py $
# $Revision: #2 $
# $DateTime: 2016/03/27 13:56:56 $
# Last checked in by: $Author: starritt $
#

from setuptools import setup

import re
with open('scram/__init__.py', 'r') as f:
    version = re.search(r'__version__ = "(.*)"', f.read()).group(1)

setup(
    name='scram',
    version=version,
    packages=['scram'],
    install_requires=[
        'enum34>=1.1.1',
        'click>=6.2',
        'pyepics>=3.2.4'
# zmq
    ],
    entry_points={
        'console_scripts': ['run_scram=scram.startup:run' ]
    }
)

# end

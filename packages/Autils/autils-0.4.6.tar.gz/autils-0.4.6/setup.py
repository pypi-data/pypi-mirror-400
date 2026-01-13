import codecs
import os
import sys
from autils import __version__

try:
	from setuptools import setup, find_packages
except:
	from distutils.core import setup

def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()



setup(
    name = "Autils",
    version = __version__,
    description = "A hepler tools for kevin kong",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    classifiers =
	[
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
		'Topic :: Scientific/Engineering :: Astronomy',
		'Topic :: Scientific/Engineering :: GIS',
		'Topic :: Scientific/Engineering :: Mathematics',
		'Intended Audience :: Science/Research',
		'Intended Audience :: Developers',
		'Intended Audience :: Information Technology',
    ],
    keywords = "Autils",
    author = "blackcat",
    author_email = "kfx2007@163.com",
    url ="https://github.com/block-cat/autils",
    license = "GNU",
    packages = find_packages(),
    include_package_data= True,
    install_requires=[
        'requests',
        'pyotp',
        'pytz',
        'python-dateutil'
    ],
    setup_requires=[
        'requests',
        'pyotp',
        'pytz',
        'python-dateutil'
    ],
    zip_safe= True,
)
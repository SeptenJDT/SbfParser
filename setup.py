from setuptools import setup, Extension
from Cython.Build import cythonize
import os

# Get the directory containing setup.py
setup_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(setup_dir, 'src')

# Define the extensions
ext_modules = [
    Extension(
        'sbf_parser.memory',
        ['sbf_parser/memory.pyx'],
        include_dirs=[setup_dir, src_dir],
        language='c'
    ),
    Extension(
        'sbf_parser.block_parsers',
        ['sbf_parser/block_parsers.pyx'],
        include_dirs=[setup_dir, src_dir],
        language='c'
    ),
    Extension(
        'sbf_parser.parser',
        ['sbf_parser/parser.pyx', 'sbf_parser/c_crc.c'],
        include_dirs=[setup_dir, src_dir],
        language='c'
    ),
    Extension(
        'sbf_parser.encoder',
        ['sbf_parser/encoder.pyx', 'sbf_parser/c_crc.c'],
        include_dirs=[setup_dir, src_dir],
        language='c'
    ),
]

# Set Cython directives
for e in ext_modules:
    e.cython_directives = {
        'language_level': "3",
        'boundscheck': False,
        'wraparound': False,
        'initializedcheck': False,
        'nonecheck': False,
    }

setup(
    ext_modules=cythonize(ext_modules)
) 

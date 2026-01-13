from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import os
import sys
import subprocess

class BuildExt(build_ext):
    def build_extensions(self):
        opts = []
        link_opts = []
        
        if sys.platform == 'win32':
            opts.extend([
                '/O2',
                '/GL',
                '/EHsc',
                '/std:c++11',
                '/MD',
                '/W3',
            ])
            link_opts.extend(['/LTCG'])
        else:
            opts.extend([
                '-O3',
                '-std=c++11',
                '-fPIC',
                '-Wall',
            ])
        
        for ext in self.extensions:
            ext.extra_compile_args = opts
            ext.extra_link_args = link_opts
        build_ext.build_extensions(self)

module = Extension(
    'pycpplink._core',
    sources=['pycpplink/advanced_low_level.cpp'],
    language='c++',
    define_macros=[('_WIN32', '1')] if sys.platform == 'win32' else [],
)

setup(
    name='PyCppLink',
    version='0.1.0',
    description='Python wrapper for advanced C++ low-level operations',
    long_description='A Python library that provides direct access to advanced C++ functionality including memory pools, data processing, and error handling.',
    long_description_content_type='text/plain',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/mcjava20/Pycpplink',
    packages=['pycpplink'],
    ext_modules=[module],
    cmdclass={'build_ext': BuildExt},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: C++',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.7',
    zip_safe=False,
)

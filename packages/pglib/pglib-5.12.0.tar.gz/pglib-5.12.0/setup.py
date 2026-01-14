#!/usr/bin/env python3

import sys
import os
import re
import subprocess
import sysconfig
from os.path import join, abspath, dirname

from setuptools import setup, Extension


def _get_osx_sdkpath():
    """
    Use xcodebuild to find the latest installed OS X SDK and return the path to it.
    """
    output = subprocess.check_output(['xcodebuild', '-version', '-sdk']).strip().decode('utf-8')

    highest = (0, 0)
    path = None

    resection = re.compile(r'^.*- (?:OS X|macOS) (\d+)\.(\d+)')
    repath = re.compile('^Path: ([^\n]+)', re.MULTILINE)

    for section in output.split('\n\n'):
        match = resection.match(section)
        if not match:
            continue

        version = tuple(int(g) for g in match.groups())
        if version > highest:
            highest = version
            path = repath.search(section).group(1)

    if highest == (0, 0):
        sys.exit('No OS X SDKs installed?  xcodebuild returned {!r}'.format(output))

    return path


def _get_files():
    return [join('src', f) for f in os.listdir('src') if f.endswith('.cpp')]


def _get_settings():
    settings = {'define_macros': []}

    # Custom build options
    for option in ['assert', 'trace', 'leak-check']:
        try:
            sys.argv.remove('--%s' % option)
            settings['define_macros'].append(('PGLIB_%s' % option.replace('-', '_').upper(), 1))
        except ValueError:
            pass

    if os.name == 'nt':
        settings['extra_compile_args'] = [
            '/Wall',
            '/wd4668',
            '/wd4820',
            '/wd4711',     # function selected for automatic inline expansion
            '/wd4100',     # unreferenced formal parameter
            '/wd4127',     # "conditional expression is constant" testing compilation constants
            '/wd4191',     # casts to PYCFunction which doesn't have the keywords parameter
        ]

        if '--debug' in sys.argv:
            sys.argv.remove('--debug')
            settings['extra_compile_args'].extend('/Od /Ge /GS /GZ /RTC1 /Wp64 /Yd'.split())

        settings['libraries'] = ['libpq', 'Ws2_32']

    elif sys.platform == 'darwin':
        sdkpath = _get_osx_sdkpath()

        settings['include_dirs'] = [
            join(sdkpath, 'usr', 'include'),
            abspath(dirname(sysconfig.get_config_h_filename().strip())),
            subprocess.check_output(['pg_config', '--includedir']).strip().decode('utf-8')
        ]
        settings['library_dirs'] = [subprocess.check_output(['pg_config', '--libdir']).strip().decode('utf-8')]
        settings['libraries'] = ['pq']

        settings['define_macros'].append(('MAC_OS_X_VERSION_10_7',))

        settings['extra_compile_args'] = ['-Wall']

    else:
        # Other posix-like: Linux, Solaris, etc.
        settings['include_dirs'] = [subprocess.check_output(['pg_config', '--includedir']).strip().decode('utf-8')]
        settings['library_dirs'] = [subprocess.check_output(['pg_config', '--libdir']).strip().decode('utf-8')]
        settings['libraries'] = ['pq']

        settings['extra_compile_args'] = ['-Wno-write-strings']

    return settings


setup(
    ext_modules=[Extension('_pglib', _get_files(), **_get_settings())],
)

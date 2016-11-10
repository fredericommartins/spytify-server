#!/usr/bin/env python

from cx_Freeze import setup, Executable
from os import getcwd, path
from shutil import rmtree
from sys import argv, platform


def SetupBuild():

    app = 'administration-console'
    base = 'Win32GUI' if platform == 'win32' else None
    curpath = path.dirname(path.realpath(argv[0]))
    filpath = path.join(curpath, 'Others')
    apppath = path.join(curpath, app)

    build_options = {'include_files': [filpath + '/icon.ico']}

    setup(
        name = app,
        version = '1.0',
        description = 'Music Streaming Service',
        options = {'build_exe': build_options},
        executables = [Executable(apppath + '.py', base = base, icon = filpath + '/icon.ico')])


SetupBuild()

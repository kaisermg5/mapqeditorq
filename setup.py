#! /usr/bin/env python3

import sys
import os

version = 'alpha 0.1'
scripts = ['mqeq.py']

data_files = ['resources']

build_exe_options = {'packages': ['os', 'PyQt5', 'PIL', 'mapqeditorq'],
                     'includes': ['sip'],
                     'excludes': 'tkinter',
                     'include_files': data_files,
                     }

executables = []
base = None
if sys.platform == 'win32':
    base = 'Win32GUI'


if '--no-freeze' not in sys.argv:
    try:
        from cx_Freeze import setup, Executable

        for script in scripts:
            executables.append(Executable(script, base=base, icon=os.path.abspath('resources/mqeq-icon.ico')))
    except ImportError:
        print('cx_Freeze not found. Using distutils instead.')
else:
    sys.argv.remove('--no-freeze')


if 'setup' not in locals():
    from distutils.core import setup

module_init = 'mapqeditorq/__init__.py'
if not os.path.exists(module_init):
    f = open(module_init, 'w')
    f.close()


setup(name='MQEQ - Map Editor',
      version=version,
      description='Map Editor for The Legend of Zelda, the Minish Cap game',
      author='Kaiser de Emperana (Mauro B.)',
      url='https://github.com/kaisermg5/mapqeditorq',
      options={"build_exe": build_exe_options},
      requires=['sip', 'PyQt5', 'PIL'],
      scripts=scripts,
      packages=['mapqeditorq'],
      executables=executables
      )


# For those windows users, that are too lazy to install python

import sys
import os


def hacky_interpreter(script, *args):
    script_globals = {}
    script_locals = {}
    exec('# Hack!', script_globals, script_locals)
    script_globals['__builtins__']['__name__'] = '__main__'

    with open(script) as f:
        contents = f.read()

    old_path = sys.path
    old_argv = sys.argv
    sys.path = [os.path.dirname(os.path.abspath(script)), *old_path]
    sys.argv = [script, *args]
    exec(contents, script_globals, script_locals)
    sys.path = old_path
    sys.argv = old_argv


if __name__ == '__main__' and len(sys.argv) > 1:
    hacky_interpreter(*(sys.argv[1::]))


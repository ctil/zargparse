# Zargparse

Usage
------
Pass a python script to zargparse.py and it will write out a Zsh completion
file to the current working directory. Make sure the script is executable
under the current environment with Python 3 since zargparse needs to run the
script.

```commandline
./zargparse.py examples/future
```

It is recommended to use [Pipenv](https://docs.pipenv.org) to build a virtual environment.

```commandline
pipenv install
pipenv run ./zargparse.py examples/future
```

Dependencies
------------
Zargparse requires Python 3 and the Jinja2 library. It has been tested with
Python 3.6.

Limitations
-----------
The tool does support complex completions of arguments as described
[here](https://github.com/zsh-users/zsh-completions/blob/master/zsh-completions-howto.org#main-utility-functions-for-overall-completion).
The completion file may need to be modified by hand after generation in order
to fine tune the completions.

Nested [sub-commands](https://docs.python.org/3.6/library/argparse.html#sub-commands)
are not supported.

Positional arguments are not yet supported.

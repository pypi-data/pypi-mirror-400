import sys


def eprint(*args, **kargs):
    """Print to stderr

    Usage::

      eprint("Hello world!")
    """
    print(*args, **kargs, file=sys.stderr)

import inspect
import os


def get_file_dir():
    """
    Usage::

      path = file_dir()
    """
    caller_frame = inspect.stack()[1]
    caller_path = caller_frame.filename
    return os.path.dirname(os.path.realpath(caller_path))

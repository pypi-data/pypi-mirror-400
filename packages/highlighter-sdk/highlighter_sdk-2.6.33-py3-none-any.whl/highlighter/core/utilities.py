import hashlib
import os
import re
from contextlib import contextmanager


def sha512_of_content(content):
    sha512 = hashlib.sha512()
    sha512.update(content)
    return sha512.hexdigest()


def get_slug(name) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def stringify_if_not_null(attribute):
    return str(attribute) if attribute is not None else None


@contextmanager
def change_dir(path):
    """Context manager that changes to a directory and returns to the original on exit.

    Args:
        path: Path to change to (str or Path)

    Example:
        with change_dir('/tmp'):
            # Do work in /tmp
            print(os.getcwd())  # /tmp
        # Back to original directory
    """
    original_dir = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(original_dir)

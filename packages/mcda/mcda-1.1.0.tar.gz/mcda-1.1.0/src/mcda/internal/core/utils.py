"""This module contains utility functions for contributors.
"""
import re
from importlib.metadata import version
from typing import Callable, Tuple, TypeVar

T = TypeVar("T")


def set_module(module: str) -> Callable[[T], T]:
    """Decorate class to change its module prefix in the name.

    This is intended for the doc, so that objects defined internally can
    appear in the public API, with all links to decorated objects going there.

    :param module: target module
    :return: decorated object
    """

    def decorated(func: T) -> T:
        func.__module__ = module
        return func

    return decorated


def package_version(
    package: str,
) -> Tuple[int, ...]:  # pragma: nocover
    """Return version of package as integers (only major, minor, patch).

    :param package:
    :raises ValueError: if `package` doesn't follow semantic versioning
    :return: package version as a tuple
    """
    v_str = version(package)
    res = re.search(r"^([0-9]+)\.([0-9]+)\.([0-9]+)", v_str)
    if res is None:
        raise ValueError(
            f"'{package}' doesn't follow semantic versioning. Got: {v_str}"
        )
    return tuple(int(v) for v in res.groups())

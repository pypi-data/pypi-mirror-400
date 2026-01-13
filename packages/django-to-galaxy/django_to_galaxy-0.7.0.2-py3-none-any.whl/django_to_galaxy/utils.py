from contextlib import contextmanager
from datetime import datetime

from bioblend.galaxy.objects import wrappers
from requests_cache import install_cache, uninstall_cache

from django_to_galaxy.settings import settings


def load_galaxy_time_to_datetime(galaxy_time: str) -> datetime:
    """
    Parse str time from galaxy to datetime.

    Args:
        galaxy_time: galaxy time
    Returns:
        datetime object of the parsed string
    """
    return datetime.strptime(galaxy_time, settings.GALAXY_TIME_FORMAT)


def load_galaxy_history_time_to_datetime(galaxy_history: wrappers.History) -> datetime:
    """
    Parse time from galaxy history object to datetime.

    Args:
        galaxy_history: Galaxy history instance
    Returns:
        datetime object of the parsed string
    """
    return load_galaxy_time_to_datetime(galaxy_history.wrapped["create_time"])


def load_galaxy_invocation_time_to_datetime(
    galaxy_invocation: wrappers.Invocation,
) -> datetime:
    """
    Parse time from galaxy invocation object to datetime.

    Args:
        galaxy_invocation: Galaxy invocation instance
    Returns:
        datetime object of the parsed string
    """
    return load_galaxy_time_to_datetime(galaxy_invocation.wrapped["create_time"])


@contextmanager
def enabled_cache():
    """
    Context manager for temporarily enabling caching for all ``requests`` functions.

    This aims to be the place to set parameters for requests_cache in the future.

    Inspired from requests_cache.enabled context manager.
    """
    install_cache()
    try:
        yield
    finally:
        uninstall_cache()

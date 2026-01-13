"""Version information for MCPost package."""

__version__ = "0.1.4"

# Version components for programmatic access
VERSION_INFO = tuple(map(int, __version__.split('.')))

def get_version():
    """Get the current version string."""
    return __version__

def get_version_info():
    """Get version as a tuple of integers."""
    return VERSION_INFO
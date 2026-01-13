try:
    from importlib.metadata import version

    __version__ = version("orkg")
except Exception:
    __version__ = "unknown"

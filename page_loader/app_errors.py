"""Internal aplication errors."""


class AppInternalError(Exception):
    """Internal error class."""


class CreateDirError(AppInternalError):
    """Internal error class: create directory."""


class SavePageError(AppInternalError):
    """Internal error class: save file."""


class AppConnectionError(AppInternalError):
    """Internal error class: connection error."""

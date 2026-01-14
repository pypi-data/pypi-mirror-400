class MissingRequiredConfiguration(Exception):
    pass


class IncorrectTypePermissionConfiguration(Exception):
    pass


class ApplicationSettingsNotFound(Exception):
    """
    Exception that indicates the application settings was not found through known methods.
    """


class RequestIDModuleNotFound(Exception):
    """
    Exception that indicates the request id module was not found through known methods.
    """


class DecoratorWrongUsage(Exception):
    """
    Generic exception when a decorator is used wrongly.
    """


class EmailValidationError(Exception):
    """
    Exception that indicates Everest is down and the default validation methods will not be used.
    """

import inspect

from typing import Type

from rest_framework.exceptions import APIException


class AllowClassBehaviorAsFunction:
    """
    This class should be used when the inherited class instance should be 'called' as a function.
    It's very useful when it's necessary to initiate a PermissionClass and then add it on `permission_class`.
    """

    def __call__(self):
        """
        The __call__ method enables classes to be writen where the instances behave like functions and can be called
        like a function. When the instance is called as a function; if this method is defined,
        x(arg1, arg2, ...) is a shorthand for x.__call__(arg1, arg2, ...).

        Google Recaptcha Permission Example:
        This method allows to use this Permission Class with a custom response without being forced to use
        "get_permissions".

        Without this method, is necessary to do something like this:
            def get_permissions(self) -> List:
                exc = SomeException(status.HTTP_401_UNAUTHORIZED, {"details": "Some message"})
                return [GoogleRecaptchaPermission(exc)]

        With this method, one can achieve the same result using something like this:
            permission_classes = [
                GoogleRecaptchaPermission(SomeException(status.HTTP_401_UNAUTHORIZED, {"details": "Some message"}))
            ]
        """

        return self


def is_exception_related_to_api_exception(
    exception_in_case_of_failed_verification: APIException | Type[APIException],
) -> bool:
    """
    Checks if the received exception is an instance or a subclass of APIException.
    The "isinstance" handles cases like this:
        class MyException(APIException):
            pass
        class MyViewset(viewsets.ModelViewSet):
            permission_class = [GoogleRecaptchaPermission(MyException())]
    While "issubclass" handles cases like this:
        class MyException(APIException):
            pass
        class MyViewset(viewsets.ModelViewSet):
            permission_class = [GoogleRecaptchaPermission(MyException)]
    """

    exc = exception_in_case_of_failed_verification
    if not exc:
        return False

    exception_class = exc if inspect.isclass(exc) else type(exc)
    # isinstance deals with initialized exceptions
    # issubclass deals with not initialized exceptions
    return isinstance(exc, APIException) or issubclass(exception_class, APIException)

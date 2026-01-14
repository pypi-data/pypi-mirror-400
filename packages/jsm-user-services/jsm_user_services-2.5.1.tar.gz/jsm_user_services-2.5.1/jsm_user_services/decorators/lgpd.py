from typing import Callable
from typing import Dict
from typing import Optional

from jsm_user_services.decorators.lgpd_utils import AnonymizeLogic
from jsm_user_services.decorators.lgpd_utils import traverse_within_dict_overriding_data
from jsm_user_services.exception import DecoratorWrongUsage


def anonymize_sensible_data(
    to_be_anonymized: Dict, raise_if_key_not_found: Optional[bool] = True, traverse_dict_pattern: Optional[str] = "__"
):
    """
    Method to be used as decorator that will anonymize sensible data, according to LGPD.

    In order to use it, the "original_method" MUST return a dict. Example:
    >>> @anonymize_sensible_data({"name": AnonymizeLogic.NAME})
    ... def honest_test():
    ...    return {"name": "Lucas Gigek Carvalho"}
    ...
    >>> honest_test()
        {"name": "Lucas C"}

    It also should be called with a dict that follows this pattern:
    {"field_that_must_be_anonymized": "anonimyze_logic_for_specific_field"}

    If the dict is more complex than the example above, use "__" to traverse within dicts/lists. Example:
    - For {"userdata": {"name": "xpto"}}, use "userdata__name";
    - For {"result": [{"userdata": {"name": "xpto"}, {"userdata": {"name": "xpto2"}]}, use "result__userdata__name";
    Example:
    >>> @anonymize_sensible_data({"userdata__name": AnonymizeLogic.NAME})
    ... def honest_test():
    ...    return {"userdata": {"name": "Lucas Gigek Carvalho"}}
    ...
    >>> honest_test()
        {"userdata": {"name": "Lucas C"}}

    It's possible to customize if it should raise or not if some key wasn't found via param "raise_if_key_not_found".
    It's possible to customize the pattern to traverse the dict as well. The default value is "__".
    """

    def wrapper(method_that_uses_the_decorator: Callable):
        """
        Since the decorator must be called with a parameter, this method is executed when the module is imported. It
        checks if "to_be_anonymized" is valid. A valid param must:
        - be a dict;
        - have keys that are a string;
        - have values that are AnonymizeLogic;
        If the criteria above is violated, raises DecoratorWrongUsage

        After that, simply return the main logic, which will be executed when the method is invoked.
        """

        if not isinstance(to_be_anonymized, dict):
            raise DecoratorWrongUsage("Please, pass a dict as param.")

        for key, value in to_be_anonymized.items():
            if not isinstance(key, str):
                raise DecoratorWrongUsage("The keys must be a str, got key %s of type %s", key, type(key))
            if not isinstance(value, Callable) or not hasattr(AnonymizeLogic, value.__name__):  # type: ignore
                raise DecoratorWrongUsage("The values must be a AnonymizeLogic, got value %s", value)

        def main_logic(*args, **kwargs):
            """
            Method that will be executed only when the method with decorator is called. Given a field to be
            anonymized (key) and the logic that it should use (value), it anonymizes the dict to be in agreement with
            LGPD.
            """

            original_result = method_that_uses_the_decorator(*args, **kwargs)

            if not isinstance(original_result, dict) and not isinstance(original_result, list):
                raise DecoratorWrongUsage(
                    "The method must return a dict or a list, but returned type %s", type(original_result)
                )

            for path, strategy in to_be_anonymized.items():
                traverse_within_dict_overriding_data(
                    path, original_result, strategy, raise_if_key_not_found, traverse_dict_pattern
                )

            return original_result

        return main_logic

    return wrapper

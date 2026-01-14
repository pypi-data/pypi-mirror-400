from enum import Enum
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional

from jsm_user_services.exception import DecoratorWrongUsage


class AnonymizeLogic(Enum):
    """
    An Enum that allows decorator's user decide which logic should be used.
    """

    @staticmethod
    def anonymize_name(name: Optional[str]):
        """
        Anonymize strategy for "name" type. It uses the following logic:
        >>> anonymize_name("Lucas Gigek Carvalho")
            Lucas C

        In order to do it, the name must be a string.
        """

        if name is None:
            return None

        if not isinstance(name, str):
            raise DecoratorWrongUsage("Name must be a string, but got %s", type(name))

        splitted_name = name.split(" ")
        if len(splitted_name) == 1:
            return name

        return f"{splitted_name.pop(0)} {splitted_name.pop()}"

    @staticmethod
    def anonymize_cpf(cpf: Optional[str]):
        """
        Anonymize strategy for "CPF" type. It uses the following logic:
        >>> anonymize_cpf("12345678910")
            *******8910

        In order to do it, the cpf must be a string.
        """

        if cpf is None:
            return None

        if not isinstance(cpf, str):
            raise DecoratorWrongUsage("CPF must be a string, but got %s", type(cpf))

        return cpf[slice(-4, None)].rjust(len(cpf), "*")

    @staticmethod
    def anonymize_phone(phone: Optional[str]):
        """
        Anonymize strategy for "phone" type. It uses the following logic:
        >>> anonymize_phone("5511912345678")
            *********5678

        In order to do it, the phone must be a string.
        """

        if phone is None:
            return None

        if not isinstance(phone, str):
            raise DecoratorWrongUsage("Phone must be a string, but got %s", type(phone))

        return phone[slice(-4, None)].rjust(len(phone), "*")

    @staticmethod
    def anonymize_email(email: Optional[str]):
        """
        Anonymize strategy for "email" type. It uses the following logic:
        >>> anonymize_email("lucas.carvalho@juntossomosmais.com.br")
            l*************@juntossomosmais.com.br

        In order to do it, the email must be a string.
        """

        if email is None:
            return None

        if not isinstance(email, str):
            raise DecoratorWrongUsage("Email must be a string, but got %s", type(email))

        splitted_email = email.split("@")

        username = splitted_email[0][slice(1)].ljust(len(splitted_email[0]), "*")
        if len(splitted_email) == 1:
            return username

        return f"{username}@{splitted_email[1]}"

    @staticmethod
    def anonymize_address_should_not_be_returned(address_data: Optional[str]):
        """
        Anonymize strategy for "address" type which shouldn't be returned. It uses the following logic:
        >>> anonymize_address_should_not_be_returned("Av. Gomes de Carvalho")
            None
        """

        return None

    @staticmethod
    def anonymize_address_should_be_returned(address_data: Optional[str]):
        """
        Anonymize strategy for "address" type which should be returned. It uses the following logic:
        >>> anonymize_address_should_be_returned("São Paulo")
            "São Paulo"
        """

        return address_data

    NAME = anonymize_name
    CPF = anonymize_cpf
    PHONE = anonymize_phone
    EMAIL = anonymize_email
    ADDRESS_CITY = anonymize_address_should_be_returned
    ADDRESS_STATE = anonymize_address_should_be_returned
    ADDRESS_NEIGHBORHOOD = anonymize_address_should_not_be_returned
    ADDRESS_STREET = anonymize_address_should_not_be_returned
    ADDRESS_NUMBER = anonymize_address_should_not_be_returned
    ADDRESS_COMPLEMENT = anonymize_address_should_not_be_returned
    ADDRESS_POSTAL_CODE = anonymize_address_should_not_be_returned


def traverse_within_dict_overriding_data(
    path: str,
    original_data: Dict | List,
    anonymize_logic: Callable,
    raise_if_key_not_found: bool,
    traverse_dict_pattern: str,
):
    """
    Method that navigates through the dict and modifies the necessary keys.
    """

    path_to_traverse = path.split(traverse_dict_pattern)

    # by doing this, all changes made on "current_key" will go to "original_data" as well
    current_key = original_data

    while len(path_to_traverse) > 0:
        if isinstance(current_key, list):
            # iterating on each item to deal with them recursively
            for item in current_key:
                traverse_within_dict_overriding_data(
                    traverse_dict_pattern.join(path_to_traverse),
                    item,
                    anonymize_logic,
                    raise_if_key_not_found,
                    traverse_dict_pattern,
                )
            # data was already changed on inner iterations, there's no need to continue the loop
            break

        next_key = path_to_traverse.pop(0)

        # If it's not a dict, it's not possible to use ".get" on it.
        if not isinstance(current_key, dict):
            continue

        # If it's the last key, the only thing that must be done is change it's data.
        # Also, it's necessary to check that the key exists, in order to not creat an additional key.
        if len(path_to_traverse) == 0 and current_key.get(next_key):
            # calling method that will anonymize data
            current_key[next_key] = anonymize_logic(current_key.get(next_key))
            # data was already changed, there's no need to continue the loop
            break

        try:
            current_key = current_key[next_key]
        except KeyError:
            if raise_if_key_not_found:
                raise DecoratorWrongUsage("Key not found %s", next_key)

    return original_data

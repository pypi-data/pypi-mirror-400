"""
err.py

module for custom errors used by UtilityCloudAPIWrapper.py
"""

from requests import RequestException


class InvalidRequestMethod(RequestException):
    ...


class InvalidConfigError(Exception):
    ...


class MissingConfigError(InvalidConfigError):
    ...


class InvalidUtilityCloudUserName(Exception):
    ...


class AuthenticationError(Exception):
    ...


class MissingMandatoryAttributeError(AttributeError):
    def __init__(self, msg: str = None, missing_mandatory_attrs: list = None, class_name: str = None):
        self.msg = msg
        self.missing_mandatory_attrs = missing_mandatory_attrs
        self.class_name = class_name
        if not self.msg:
            if not self.missing_mandatory_attrs or not self.class_name:
                raise ValueError("Missing mandatory attributes "
                                 "or class_name for "
                                 "MissingMandatoryAttributeError, and msg not provided")
            self.msg = f"{','.join(self.missing_mandatory_attrs)} must be set for {self.class_name}"
        super().__init__(self.msg)

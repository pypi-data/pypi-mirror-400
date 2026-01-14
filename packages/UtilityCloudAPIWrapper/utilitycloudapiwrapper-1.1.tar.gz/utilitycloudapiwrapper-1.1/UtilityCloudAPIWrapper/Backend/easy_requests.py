from json import JSONDecodeError, loads as jloads
from logging import Logger

import requests

from UtilityCloudAPIWrapper.Backend import InvalidRequestMethod


class EasyReq:
    TOO_MANY_REQUESTS_REASON = "Too many requests sent too quickly"
    VALID_REQUEST_METHODS = ["GET", "POST"]
    HTTP_400s = {403, 401}

    def __init__(self, logger: Logger = None, fail_http_400s: bool = True):
        self._fail_http_400s = fail_http_400s
        self._logger = logger if logger else Logger("Dummy_logger")

    def make_request(self, method: str, url: str, headers: dict, payload) -> requests.Response:
        self._validate_request_method(method)
        try:
            response = requests.request(method, url, headers=headers, data=payload)
            return self._handle_response(response)
        except requests.RequestException as e:
            self._logger.error(e, exc_info=True)
            raise

    def _validate_request_method(self, method: str):
        if method.upper() not in self.VALID_REQUEST_METHODS:
            valid_methods = ", ".join(self.VALID_REQUEST_METHODS)
            raise InvalidRequestMethod(
                f"{method} is not a valid request method (Options are: {valid_methods})"
            )

    def _handle_response(self, response: requests.Response) -> requests.Response:
        try:
            loaded = jloads(response.text.split('}')[0] + '}')
        except JSONDecodeError:
            loaded = {}
        if response.ok and 'error' not in loaded:
            return response
        if response.status_code == 429:
            response.reason = self.TOO_MANY_REQUESTS_REASON
        return self._process_error_response(response, loaded_error=loaded)

    def _process_error_response(self, response: requests.Response, **kwargs) -> requests.Response:
        try:
            error_message = self._extract_error_message(response, **kwargs)
            raise requests.RequestException(f"Response was {response.status_code} {response.reason}, "
                                            f"with message: {error_message}")
        except requests.RequestException as e:
            self._logger.error(e, exc_info=True)
            if not self._fail_http_400s and response.status_code in self.__class__.HTTP_400s:
                self._logger.warning(
                    f"Response code {response.status_code} returned. Returning response for further processing.")
                return response
            raise e

    @staticmethod
    def _extract_error_message(response: requests.Response, **kwargs) -> str:
        try:
            return response.json().get('message', '').split('Authorization=')[0]
        except JSONDecodeError:
            loaded_error = kwargs.get('loaded_error', {})
            if loaded_error:
                return loaded_error.get('error')

            return response.text.split('Authorization=')[0]

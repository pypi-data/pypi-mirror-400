from json import dumps as jdumps
from logging import Logger

from EasyLoggerAJM import EasyLogger
from requests import JSONDecodeError

from UCWrapBetterConfig import UCWrapBetterConfig
from UtilityCloudAPIWrapper.Backend import _UtilityCloudAuth, EasyReq, AuthenticationError


class _WrapperInitializer(_UtilityCloudAuth):
    BASE_URL_DEFAULT = "https://api.ucld.us/env/prd/"
    MODULE_NAME = __file__.rsplit('\\', maxsplit=1)[-1].split(".")[0]

    def __init__(self, logger: Logger = None, **kwargs):
        self._logger = self.init_logger(logger=logger, **kwargs)

        self.base_url = kwargs.get('base_url', self.__class__.BASE_URL_DEFAULT)

        self.config = self.pre_init_config(**kwargs)
        kwargs.pop('config', None)
        self.ER = EasyReq(logger=self._logger, fail_http_400s=True)
        super().__init__(requester=self.ER, logger=self._logger, config=self.config, **kwargs)

        self.base_headers = {
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.8',
            'Authorization': self.auth
        }
        self.base_query = {
            "page": 1,
            "itemCount": "10",
            "search": "",
            "SearchFacets": "",
            "orderby": None,
            "isAdvanced": True,
            "filters": None,
            "isactive": True,
            "facets": ""
        }

    def init_logger(self, **kwargs):
        if logger := kwargs.get('logger'):
            return logger
        else:
            return EasyLogger(project_name=kwargs.get('logger_project_name', self.__class__.MODULE_NAME),
                              log_spec=kwargs.get('log_spec', 'hourly'),
                              show_warning_logs_in_console=True).logger

    def pre_init_config(self, **kwargs):
        if hasattr(self, 'config') and self.config:
            self.init_config()
        else:
            config_filename = kwargs.get('config_filename', f"{self.__class__.MODULE_NAME}ConfigAJM.ini")
            self.config = UCWrapBetterConfig(config_dir="../cfg",
                                             config_filename=config_filename)

            self.config.GetConfig()
            self.init_config()
        return self.config
        #kwargs['config'] = self.config

    def init_config(self):
        self.config['DEFAULT']['base_url'] = self.base_url
        self._logger.info("Attempting to write base_url to config...")
        if hasattr(self.config, "config_location"):
            with open(self.config.config_location, 'w') as f:
                self._logger.debug(f"Writing Config to {self.config.config_location}")
                self.config.write(fp=f)
        else:
            self._logger.warning("Config could not be written to "
                                 "since there is no config.config_location parameter.")

    def _check_auth(self):
        if not self.auth_initialized:
            self._log_and_raise(AuthenticationError, "self.RunAuth must be run before making requests.")
        else:
            self.base_headers['Authorization'] = self.auth
            return

    def _print_response(self, res):
        try:
            print(jdumps(res.json(), indent=4))
        except JSONDecodeError as e:
            self._logger.warning(e)
            print(res.text)

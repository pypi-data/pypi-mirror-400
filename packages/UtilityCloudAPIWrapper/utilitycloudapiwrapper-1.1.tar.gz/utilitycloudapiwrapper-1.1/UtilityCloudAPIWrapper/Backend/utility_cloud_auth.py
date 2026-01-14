import getpass
from configparser import ConfigParser
from json import load as jload, dumps as jdumps, dump as jdump
from logging import Logger
from os import remove, makedirs
from os.path import join, isfile, isdir, abspath

import BetterConfigAJM as BetterConfig
import PurgeSecrets
from requests import RequestException

from UtilityCloudAPIWrapper.Backend import (InvalidConfigError,
                                            InvalidUtilityCloudUserName, MissingConfigError)


class _UtilityCloudAuth:
    CONFIG_SUFFIXES = ['cfg', 'config', 'ini']
    VALID_KEY_FILETYPES = ['json', 'config']
    DEFAULT_KEY_FORMAT = VALID_KEY_FILETYPES[0]
    AUTH_BASE_URL = "https://ucld.us/"
    EMAIL_REGEX = r'^[\w-]+@([\w-]+\.)+[\w-]{2,4}$'
    EXPIRED_ERROR_CODES = ['401', '403']

    def __init__(self, requester, logger=None, key_dirpath=None, chosen_keyfile_format=None, **kwargs):
        self.auth = None
        self.auto_auth = kwargs.get('auto_auth', False)
        self.auth_initialized = False
        self.use_config = kwargs.get('use_config', False)
        self._auth_runtype_default = kwargs.get('auth_runtype_default')
        self._auth_credentials = kwargs.get('auth_credentials')

        self.user_email_suffix = kwargs.get('user_email_suffix')
        self.check_purge = kwargs.get('check_purge', False)
        self.purge_all = kwargs.get('purge_all', False)

        self._key_dirpath = key_dirpath
        self._auth_key_filename = 'auth_key'
        self._current_keyfile_format = chosen_keyfile_format or self.DEFAULT_KEY_FORMAT

        self._logger = logger or Logger("DUMMY_LOGGER")
        self.requester = requester

        self.config = self._process_kwargs_and_get_config(kwargs)
        self._setup_key_dirpath(key_dirpath)

        if self.auto_auth:
            self._logger.debug("auto_auth is enabled. Running authentication...")
            self.auth, self.auth_initialized = self.RunAuth()
        else:
            self._logger.info("Authentication needs to be run manually or enable auto_auth.")

    def _log_and_raise(self, exception_type, message):
        self._logger.error(message, exc_info=True)
        raise exception_type(message)

    def _process_kwargs_and_get_config(self, kwargs):
        if kwargs:
            self._logger.info("__init__ kwargs detected")

        self._make_key_dirpath = kwargs.get('make_key_dirpath', True)
        if 'config' in kwargs:
            return self._validate_config(kwargs['config'])
        return None

    def _setup_key_dirpath(self, key_dirpath):
        # Prefer config-specified key_dirpath whenever a config exists,
        # regardless of the `use_config` flag. Fall back to explicit argument.
        if self.config:
            # Use AUTH.key_dirpath if present, otherwise use the passed-in key_dirpath
            self._key_dirpath = self.config["AUTH"].get("key_dirpath", key_dirpath or self._key_dirpath)
        elif self._key_dirpath is None:
            self._log_and_raise(
                InvalidConfigError,
                "Key directory path (`key_dirpath`) must be set or specified in the config."
            )

        self._key_dirpath_check()

    def _validate_config(self, config):
        if isinstance(config, BetterConfig.BetterConfigAJM):
            self._logger.info("Config validated with BetterConfig.")
            return config.GetConfig()
        if isinstance(config, ConfigParser):
            self._logger.info("Config validated with ConfigParser.")
            return config
        else:
            self._log_and_raise(InvalidConfigError,
                                f"Config must be an instance of ConfigParser or BetterConfig, not {type(config)}.")
            return None

    def expired_auth_del(self, e):
        """
        deletes the auth key if it is expired, this is determined by the error passed in.
        :param e: Exception raised during API request
        :type e: Exception
        :return: None
        :rtype: None
        """
        if any(code in e.args[0] for code in self.EXPIRED_ERROR_CODES):
            auth_key_path = join(self.config['AUTH']['key_dirpath'], f"{self._auth_key_filename}.json").replace('\\',
                                                                                                                '/')
            warning_message = f"Auth key likely expired. Deleting {auth_key_path}, retry authentication."
            self._logger.warning(warning_message)
            remove(auth_key_path)
            raise RequestException(warning_message) from None
        self._logger.error(e, exc_info=True)
        raise e

    def RunAuth(self):
        self._logger.info("Attempting to initialize Auth...")
        if self._auth_runtype_default:
            cred_args = {'runtype': self._auth_runtype_default,
                         'credentials': self._auth_credentials} if self._auth_credentials else {
                'runtype': self._auth_runtype_default}
            self.auth = self._InitAuth(**cred_args)
        else:
            self.auth = self._InitAuth()

        if self.auth:
            self.auth_initialized = True
            self._logger.info("Authentication initialized successfully.")
        return self.auth, self.auth_initialized

    def _get_uc_login(self, **kwargs):
        def _email_check(candidate):
            import re
            email_pattern = re.compile(self.EMAIL_REGEX)
            res = re.fullmatch(email_pattern, candidate)
            return res

        def _get_user_loop():
            while True:
                user = input("UC Username: ")
                if user:
                    if self.user_email_suffix:
                        if not user.endswith(self.user_email_suffix):
                            user = user + self.user_email_suffix
                            return user
                    elif not self.user_email_suffix and not _email_check(user):
                        try:
                            raise InvalidUtilityCloudUserName("Invalid username format, please use your full email!")
                        except InvalidUtilityCloudUserName as e:
                            print(e)
                            self._logger.warning(e, exc_info=True)
                    if _email_check(user):
                        return user

        def _get_pass_loop():
            print(f"username: {user}")
            while True:
                password = getpass.getpass("Password: ")
                if password:
                    return password

        user = None
        password = None
        override_config_to_edit = False

        if kwargs:
            self._logger.debug("kwargs used in _get_uc_login.")
            if 'override_config_to_edit' in kwargs:
                override_config_to_edit = kwargs['override_config_to_edit']

        if not self.use_config or not self.config["AUTH"]["user"]:
            user = _get_user_loop()

        # if not self.use_config OR IF OVERRIDE_CONFIG_TO_EDIT IS TRUE
        if not self.use_config or override_config_to_edit:
            if not user:
                user = self.config['AUTH']["user"]
            else:
                self.config["AUTH"]["user"] = user
            password = _get_pass_loop()
            if password:
                if self.use_config:
                    self.config['AUTH']["password"] = password
                    user = self.config['AUTH']["user"]
                    if hasattr(self.config, "config_location"):
                        with open(self.config.config_location, 'w') as f:
                            self.config.write(f)
                    else:
                        self._logger.warning("Config could not be written to "
                                             "since there is no config.config_location parameter.")

        if self.use_config and not override_config_to_edit:
            if self.config and self.use_config:
                if not user:
                    user = self.config['AUTH']["user"]
                self.config["AUTH"]['user'] = user
                if self.user_email_suffix is not None and self.config['AUTH']["user"].endswith(self.user_email_suffix):
                    pass
                else:
                    if not user:
                        user = self.config['AUTH']["user"] + self.user_email_suffix
                try:
                    if not self.config['AUTH']["password"] or self.config['AUTH']["password"] == '':
                        self._get_uc_login(override_config_to_edit=True)
                    password = self.config['AUTH']["password"]
                except KeyError as e:
                    self._get_uc_login(override_config_to_edit=True)
                    password = self.config['AUTH']["password"]

            else:
                self._log_and_raise(MissingConfigError, "self.Config must be set in order to use config file.")

        if user and password:
            return user, password
        else:
            self._log_and_raise(AttributeError, "Both user and password cannot be None.")

    def _InitAuth(self, **kwargs):
        def _runtype_read_logic():
            self._logger.info("attempting to read auth key")
            if (self.full_keypath.endswith("json") or
                    [x for x in self.CONFIG_SUFFIXES if self._full_keypath.endswith(x)]):
                if isfile(self.full_keypath):
                    self._logger.info(f"{self.full_keypath} detected, reading.")
                    self.auth = self.ReadAuth(self._full_keypath)
                else:
                    self._logger.info(f"{self.full_keypath} not detected, attempting to request new auth.")
                    user, password = self._get_uc_login(use_config=self.use_config)
                    self.auth = self.ReqNewAuth(username=user, password=password)
            else:
                self._log_and_raise(FileNotFoundError, f"{self.full_keypath} could not be found.")

            return self.auth

        def _runtype_req_logic():
            self._logger.info("requesting new auth key")
            if 'username' in credentials.keys() and 'password' in credentials.keys():
                self._logger.info("logging in with credentials")
                self.auth = self.ReqNewAuth(credentials['username'], credentials['password'])
            else:
                self._logger.info("logging in with credentials")
                user, password = self._get_uc_login(use_config=self.use_config)
                self.auth = self.ReqNewAuth(user, password)
            return self.auth

        runtype = None
        credentials = None
        if kwargs:
            if 'runtype' in kwargs or runtype is not None:
                runtype = kwargs['runtype']
                if runtype not in ['read', 'req_new']:
                    self._log_and_raise(AttributeError, 'runtype attribute not recognized')
            else:
                self._log_and_raise(AttributeError, 'runtype attribute not given!')

            if 'credentials' in kwargs and isinstance(kwargs['credentials'], dict):
                credentials = kwargs['credentials']
            else:
                if runtype == 'read':
                    pass
                else:
                    self._log_and_raise(AttributeError, f'Credentials needed for runtype {runtype}')

        self._logger.info(f"runtype detected as {runtype or 'runtype is None'}")

        if runtype == 'read':
            self.auth = _runtype_read_logic()

        elif runtype == 'req_new':
            self.auth = _runtype_req_logic()

        elif not runtype:
            self._logger.info("no runtype detected, defaulting to \'read\' mode.")
            self.auth = _runtype_read_logic()
        return self.auth

    def _key_dirpath_check(self):
        try:
            if not isdir(self._key_dirpath) and self._make_key_dirpath:
                makedirs(self._key_dirpath)
                self._logger.info(f"{self._key_dirpath} created.")
            elif isdir(self._key_dirpath):
                self._logger.info(f"{self._key_dirpath} detected.")
                pass
            else:
                self._log_and_raise(NotADirectoryError, f"{self._key_dirpath} does not exist,  "
                                                        f"and self._make_key_dirpath kwarg is set to false")
        except TypeError as e:
            self._log_and_raise(ValueError, f"_key_dirpath is {self._key_dirpath}, this folder cannot be created."
                                            f"Please use the key_dirpath attribute if key_dirpath "
                                            f"is not part of your config file.")

    @property
    def key_dirpath(self):
        return self._key_dirpath

    @key_dirpath.setter
    def key_dirpath(self, value):
        self._key_dirpath = value

    @property
    def full_keypath(self):
        self._full_keypath = (join(self.key_dirpath, self._auth_key_filename).replace("\\", "/")
                              + '.' + self._current_keyfile_format)
        return self._full_keypath

    def ReadAuth(self, key_path=None):
        def _load_auth(f_obj):
            if abspath(f_obj.name).split('.')[-1].lower() == 'json':
                loaded = jload(fp=f_obj)
                l_auth = eval(jdumps(loaded, indent=4))
                l_auth = l_auth['auth']
            elif abspath(f_obj.name).split('.')[-1].lower() in self.CONFIG_SUFFIXES:
                # TODO: implement this
                self._log_and_raise(NotImplementedError, "config is not implemented yet.")
            else:
                l_auth = f_obj.read()
            return l_auth

        if key_path:
            if isfile(key_path):
                with open(key_path) as f:
                    auth = _load_auth(f)
            else:
                user, password = self._get_uc_login(use_config=self.use_config)
                auth = self.ReqNewAuth(username=user, password=password)

        else:
            if isfile(self.full_keypath):
                if (not abspath(self.full_keypath).split('.')[-1]
                        or abspath(self.full_keypath).split('.')[-1] not in self.VALID_KEY_FILETYPES):
                    with open(self.full_keypath) as f:
                        auth = _load_auth(f)
                else:
                    with open(self.full_keypath) as f:
                        auth = _load_auth(f)
            else:
                self._log_and_raise(FileNotFoundError, "keypath file not found, try running ReqNewAuth method.")
        return auth

    def ReqNewAuth(self, username: str, password: str, ):
        self._logger.info("Getting authentication token...")
        auth_url = join(self.AUTH_BASE_URL, "api/authentication").replace("\\", "/")

        payload = jdumps({
            "UserName": username,
            "Password": password
        })
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json'
        }

        res = self.requester.make_request("POST", auth_url, headers, payload)

        auth = res.text

        self._WriteAuthToFile(file_type=self._current_keyfile_format, auth=auth)
        self._logger.info("Auth received, returning auth.")
        return auth

    def _WriteAuthToFile(self, file_type: str, auth: str = None, **kwargs):
        pw = None
        user = None

        if kwargs:
            if 'password' in kwargs:
                pw = kwargs['password']
            if 'username' in kwargs:
                user = kwargs['username']

        if file_type not in self.VALID_KEY_FILETYPES:
            self._log_and_raise(AttributeError, f"File type is not valid, use {self.VALID_KEY_FILETYPES}")
        if auth:
            if self.full_keypath:
                pass
            with open(self.full_keypath, 'w') as f:
                if file_type == 'json':
                    auth_dict = {'auth': auth}
                    # this is where the auth file is written
                    jdump(obj=auth_dict, fp=f, indent=4)
                elif file_type == 'config':
                    self._log_and_raise(NotImplementedError, "config portion is still in progress.")

        else:
            if user and pw:
                auth = self.ReqNewAuth(password=pw, username=user)
                self._WriteAuthToFile('json', auth=auth)
            else:
                self._log_and_raise(AttributeError, "User and password are required  if no auth is supplied.")

    def PurgeAuthkey(self, purge_age_minutes: int = 30, **kwargs):
        confirm_purge = kwargs.get('confirm_purge', True)

        PS = PurgeSecrets.PurgeSecrets(logger=self._logger, purge_age_minutes=purge_age_minutes)
        PS.confirm_purge = confirm_purge
        if PS.IsExpired(filepath=self._full_keypath):
            PS.PurgeFile()

    def PurgeAll(self, config_section_to_purge='AUTH',
                 config_fields_to_purge: list or None = None,
                 purge_age_minutes: int = 30, **kwargs):
        confirm_purge = True
        if kwargs:
            if 'confirm_purge' in kwargs:
                confirm_purge = kwargs['confirm_purge']

        if config_fields_to_purge is None:
            config_fields_to_purge = ['user', 'password']
        PS = PurgeSecrets.PurgeSecrets(logger=self._logger, purge_age_minutes=purge_age_minutes)
        PS.confirm_purge = confirm_purge
        PS.TotalPurge(self.config, self.config.config_location,
                      config_section_to_purge, config_fields_to_purge, filepath=self._full_keypath)

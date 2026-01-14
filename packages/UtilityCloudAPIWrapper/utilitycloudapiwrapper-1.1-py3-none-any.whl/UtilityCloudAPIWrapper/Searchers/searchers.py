import datetime
import re
import uuid
from json import dumps as jdumps, JSONDecodeError
from typing import Union, Optional, Callable, Type, Dict

from requests import Response

from UtilityCloudAPIWrapper.Backend import MissingMandatoryAttributeError, FacetSearchKeys
from UtilityCloudAPIWrapper.Searchers import _Asset, _WorkOrder, _AssetClass, _Account, _User, _Customer
from UtilityCloudAPIWrapper import _WrapperInitializer


class _CreatedDateSearchProperties:
    DEFAULT_CREATED_DATE = datetime.datetime.now()  # .strftime('%m/%d/%Y')  # '11/09/2020' known to work for testing
    DEFAULT_DATE_STR_FORMAT = '%m/%d/%Y'

    def __init__(self, **kwargs):
        self._created_date = None
        self.date_string_format = kwargs.get('date_string_format', self.__class__.DEFAULT_DATE_STR_FORMAT)
        self.created_date = kwargs.get('created_date', self.__class__.DEFAULT_CREATED_DATE)

    @classmethod
    def _validate_date_string(cls, date_string: str, valid_date_string_format, **kwargs):
        try:
            datetime.datetime.strptime(date_string, valid_date_string_format)
        except ValueError:
            raise ValueError(f"{date_string} is not a valid date string")

    @classmethod
    def created_date_equal(cls, date: str, validate_date_string=True, **kwargs):
        if validate_date_string:
            vds = {'valid_date_string_format': kwargs.get('date_string_format', cls.DEFAULT_DATE_STR_FORMAT)}
            cls._validate_date_string(date_string=date, **vds)
        return f"{FacetSearchKeys.CREATEDDATE_KEY}={date}"

    @classmethod
    def created_date_between(cls, start_date, end_date, validate_date_string=True, **kwargs):
        if validate_date_string:
            vds = {'valid_date_string_format': kwargs.get('date_string_format', cls.DEFAULT_DATE_STR_FORMAT)}
            cls._validate_date_string(date_string=start_date, **vds)
            cls._validate_date_string(date_string=end_date, **vds)

        return f"{FacetSearchKeys.CREATEDDATE_KEY} `{start_date} | {end_date}"

    @property
    def created_date(self):
        return self._created_date

    @created_date.setter
    def created_date(self, value: datetime.datetime):
        self._created_date = value.strftime(self.date_string_format)

    @property
    def seven_days_before_created_date(self):
        created_date_date_obj = datetime.datetime.strptime(
            self.created_date, self.date_string_format).date()
        return (created_date_date_obj - datetime.timedelta(days=7)).strftime(self.date_string_format)

    @property
    def one_year_before_created_date(self):
        created_date_date_obj = datetime.datetime.strptime(
            self.created_date, self.date_string_format).date()
        return (created_date_date_obj - datetime.timedelta(days=365)).strftime(self.date_string_format)


class BaseSearch(_WrapperInitializer, _CreatedDateSearchProperties):
    # Global registry of searchers keyed by class name lowercase
    _REGISTRY: Dict[str, Type['BaseSearch']] = {}

    DEFAULT_ID_TYPE_STR: str = ""
    DEFAULT_ERROR_MSG = "ID must contain only numbers."
    FULL_DEFAULT_ERROR_MSG: str = ' '.join([DEFAULT_ID_TYPE_STR, DEFAULT_ERROR_MSG])

    DEFAULT_RESULTS_COUNT_KEY: str = None

    DETAILS_URL_ENDPOINT: str = None
    QUERY_URL_ENDPOINT: str = None
    RETURNED_OBJ_TYPE: Callable = None
    MANDATORY_ATTRS = ['DEFAULT_ID_TYPE_STR', 'DETAILS_URL_ENDPOINT',
                       'RETURNED_OBJ_TYPE', 'QUERY_URL_ENDPOINT']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.query_url = self.base_url + self.__class__.QUERY_URL_ENDPOINT
        self._details_url = None
        self.results_count_key = kwargs.get('results_count_key', self.__class__.DEFAULT_RESULTS_COUNT_KEY)

    @classmethod
    def register_for_factory(cls):
        # Auto-register any subclass that defines a RETURNED_OBJ_TYPE
        if getattr(cls, 'RETURNED_OBJ_TYPE', None):
            key = cls.__name__.lower()
            BaseSearch._REGISTRY[key] = cls

    @classmethod
    def check_for_missing_mandatory_attrs(cls):
        missing_mandatory_attrs = [x for x in cls.MANDATORY_ATTRS if getattr(cls, x) in [None, ""]]
        if any(missing_mandatory_attrs):
            raise MissingMandatoryAttributeError(missing_mandatory_attrs=missing_mandatory_attrs,
                                                 class_name=cls.__name__)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()
        cls.register_for_factory()
        cls.check_for_missing_mandatory_attrs()

    @staticmethod
    def _isguid(value):
        try:
            return str(uuid.UUID(value)) == value
        except ValueError:
            return False

    @property
    def details_url(self):
        return self._details_url

    @details_url.setter
    def details_url(self, value):
        full_endpoint = f"{self.__class__.DETAILS_URL_ENDPOINT}{value}"
        self._details_url = self.base_url + full_endpoint

    def _apply_additional_query_params(self, kwargs):
        if item_count := kwargs.get('item_count'):
            if not isinstance(item_count, int) or item_count < 1:
                self._log_and_raise(ValueError, "'item_count' must be a positive integer.")
            self.base_query['ItemCount'] = str(item_count)
        if page := kwargs.get('page'):
            if not isinstance(page, int) or page < 1:
                self._log_and_raise(ValueError, "'page' must be a positive integer.")
            self.base_query['page'] = page

    # TODO: MOVE TO NEW HELPER CLASS
    def _validate_obj_id_format(self, obj_id, **kwargs):
        if not str(obj_id).isnumeric():
            self._log_and_raise(AttributeError, kwargs.get('err_msg',
                                                           self.__class__.FULL_DEFAULT_ERROR_MSG))

    def _get_id_from_input(self, **kwargs):
        id_type_str = kwargs.get('id_type_str', self.__class__.DEFAULT_ID_TYPE_STR)
        for _ in range(3):  # Retry up to 3 times
            input_id = input(f"Please enter {id_type_str} ID: ")
            if input_id:
                return input_id
        raise ValueError(f" {id_type_str} ID input failed after multiple attempts.")

    def _get_obj_id(self, obj_id=None, **kwargs):
        if obj_id is not None:
            self._validate_obj_id_format(obj_id, **kwargs)
        else:
            obj_id = self._get_id_from_input()
            self._validate_obj_id_format(obj_id, **kwargs)
        return obj_id

    def _get_obj_by_id_url(self, obj_id, **kwargs) -> str:
        self.details_url = obj_id
        url = self.details_url
        return url

    def _req_obj_by_id(self, obj_id=None, **kwargs) -> Response:
        url = self._get_obj_by_id_url(obj_id, **kwargs)
        res = self.ER.make_request("GET", url, self.base_headers, payload={})
        return res

    def _post_req_processing(self, response: Response, **kwargs):
        if kwargs.get('print_response', False):
            self._print_response(response)
        return response

    def _create_obj(self, response: Response, **kwargs):
        # noinspection PyCallingNonCallable
        return self.__class__.RETURNED_OBJ_TYPE(self._logger, **response.json())
    # TODO: END MOVE TO NEW HELPER CLASS ^^^^^

    def get_obj_by_id(self, obj_id=None, **kwargs):
        self._check_auth()
        obj_id = self._get_obj_id(obj_id=obj_id, **kwargs)

        res = self._req_obj_by_id(obj_id=obj_id, **kwargs)

        res = self._post_req_processing(res, **kwargs)

        return self._create_obj(res, **kwargs)

    def _validate_facets_string(self, facets_string: str):
        return facets_string

    def _validate_return_type(self, return_type):
        return return_type

    def _pre_query_checks(self, facets_string: str, **kwargs):
        self._check_auth()
        facets_string = self._validate_facets_string(facets_string)
        self.base_query['facets'] = facets_string
        self._logger.info(f"Adding Facet String: {facets_string}")

        search_url = kwargs.get('search_url', self.query_url)
        return_type = str(kwargs.get('return_type', '') or '').lower()
        print_response = kwargs.get('print_response', False)

        self._validate_return_type(return_type)
        return search_url, return_type, print_response

    def _log_number_of_results(self, results_dict, **kwargs):
        print_msg = kwargs.pop('print_msg', True)
        self._logger.info(f"{len(results_dict) if results_dict else 0} "
                          f"{self.__class__.DEFAULT_ID_TYPE_STR}(s) Returned", print_msg=print_msg)

    def _print_clean_and_return_query(self, res, print_response=False, **kwargs):
        self._log_number_of_results(res.json().get(self.results_count_key, None), **kwargs)
        if print_response:
            self._print_response(res)
        return res

    def query_for_objects(self, *args, **kwargs):
        search_url, return_type, print_response = self._pre_query_checks(*args, **kwargs)
        query_dict = kwargs.get('query_dict', self.base_query)

        res = self.ER.make_request("POST", search_url, headers=self.base_headers,
                                   payload=jdumps(query_dict))

        return self._print_clean_and_return_query(res, print_response, **kwargs)

    @property
    def base_facet_args(self):
        # meant to be overridden by subclasses
        return ""


class AssetSearch(BaseSearch):
    """
    AssetSearch class provides functionality to search for assets and retrieve asset details through UtilityCloudAPIWrapper.

    It contains the following attributes:
    - REAL_ID_SEARCH_URL: The URL for searching asset IDs.
    - DETAIL_SEARCH_URL: The URL for retrieving asset details.
    - RETURN_TYPE_ID: Constant for identifying return type as ID.
    - RETURN_TYPE_DETAIL: Constant for identifying return type as detail.
    - ASSETTAG_KEY: Key for identifying asset tag.
    - DESCRIPTION_KEY: Key for identifying asset description.

    The class constructor initializes the object with required parameters. It also sets up valid asset search facets.

    The 'valid_asset_search_facets' property retrieves valid asset search facets from the API.

    The 'get_assets' method searches for assets based on provided facets and returns a list of asset IDs or asset details.

    The 'get_asset_by_id' method retrieves asset details for a specific asset ID.

    The class also contains internal methods for validating facets string, return type, asset ID format, determining search URL, and applying additional query parameters.

    Additionally, there is a static method '_get_id_from_input' for inputting asset ID from the user and a method '_print_response' for printing response data.

    Note: This class heavily relies on UtilityCloudAPIWrapper for making API requests and handling responses.
    """
    REAL_ID_SEARCH_URL = 'https://ucld.us/api/AssetSearchController/read'
    DETAIL_SEARCH_URL = 'https://ucld.us/api/AssetDetailsController/GET_ASSET_DETAILS'

    RETURN_TYPE_ID = 'id'
    RETURN_TYPE_DETAIL = 'detail'

    DETAILS_URL_ENDPOINT = "asset/getassetbyid?assetid="
    QUERY_URL_ENDPOINT = "asset/getassets"
    SEARCH_FACETS_ENDPOINT = "asset/basicfilters"

    DEFAULT_RESULTS_COUNT_KEY = "data"
    DEFAULT_ID_TYPE_STR = "Asset"
    DEFAULT_ERROR_MSG = "ID must contain only numbers."
    RETURNED_OBJ_TYPE = _Asset

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._valid_asset_search_facets = None
        self._search_facets_url = self.base_url + self.__class__.SEARCH_FACETS_ENDPOINT

    @classmethod
    def get_asset_class_id_facet(cls):
        # meant to be overridden by subclasses
        return ""  #f"{cls.ASSET_CLASS_ID_KEY} : {cls.WM_ASSET_CLASS_ID}"

    @property
    def valid_asset_search_facets(self):
        if not self._valid_asset_search_facets:
            self._check_auth()
            payload = {}
            res = self.ER.make_request("get", self._search_facets_url, self.base_headers, payload)
            self._valid_asset_search_facets = None if res.text in ['', {}] else res.json()
        return self._valid_asset_search_facets

    # noinspection PyInconsistentReturns
    def _validate_facets_string(self, facets_string: str):
        if self.valid_asset_search_facets:
            if any([facets_string.startswith(x['id']) for x in self.valid_asset_search_facets]):
                return facets_string
            else:
                self._log_and_raise(ValueError, f"Invalid facets string: {facets_string}.")
        else:
            self._log_and_raise(ValueError,
                                f"No valid facets found, this could be due to an invalid/Expired auth token.")

    def _validate_return_type(self, return_type):
        valid_return_types = [AssetSearch.RETURN_TYPE_ID, AssetSearch.RETURN_TYPE_DETAIL]
        if return_type not in valid_return_types:
            self._log_and_raise(
                ValueError,
                f"Invalid return_type '{return_type}'. It must be one of {valid_return_types}."
            )

    def _pre_query_checks(self, facets_string: str, **kwargs):
        search_url, return_type, print_response = super()._pre_query_checks(facets_string, **kwargs)

        if search_url and return_type:
            self._logger.warning("return_type is also given, so search_url will be ignored.")

        search_url = self._determine_search_url(facets_string, return_type)
        self._apply_additional_query_params(kwargs)

        return search_url, return_type, print_response

    def _print_clean_and_return_query(self, res, print_response=False, **kwargs):
        res = super()._print_clean_and_return_query(res, print_response, **kwargs)
        return_type = kwargs.get('return_type', '') or ''

        try:
            return ([self.get_obj_by_id(obj_id=x['id']) for x in res.json()[self.results_count_key]]
                    if return_type == self.__class__.RETURN_TYPE_ID
                    else _Asset(self._logger, **res.json()))
        except (JSONDecodeError, IndexError) as e:
            if return_type == self.__class__.RETURN_TYPE_ID:
                self._log_and_raise(ValueError, "No ID data returned")
            else:
                self._log_and_raise(e.__class__, e)

    def _determine_search_url(self, facets_string, return_type):
        if return_type == self.__class__.RETURN_TYPE_ID:
            return self.__class__.REAL_ID_SEARCH_URL
        if return_type == self.__class__.RETURN_TYPE_DETAIL:
            if 'assetId' in self.base_query:
                return self.__class__.DETAIL_SEARCH_URL
            if facets_string.split(':')[0].strip() == FacetSearchKeys.ASSETTAG_KEY:
                self.base_query['assetId'] = facets_string.split(':')[-1].strip()
                return self.__class__.DETAIL_SEARCH_URL
            self._log_and_raise(AttributeError, "'assetId' not found in self.base_query")
        return None

    def get_assets(self, facets_string: str, **kwargs) -> Union[list, _Asset]:
        return self.query_for_objects(facets_string, **kwargs)


class CustomerSubSearcher(AssetSearch):
    DEFAULT_ID_TYPE_STR = "CustomerAsset"
    RETURNED_OBJ_TYPE = _Customer
    CUSTOMERS_CLIENT_ID = "a2c6c98b-f04e-472a-96d2-0fe8cbc5023a"
    CUSTOMERS_ASSET_CLASS_ID = 55417493

    @classmethod
    def _is_customer_asset(cls, response: Response):
        return response.json().get(FacetSearchKeys.CLIENT_ID_KEY.value, None) == cls.CUSTOMERS_CLIENT_ID

    @classmethod
    def get_client_id_facet(cls):
        return f"{FacetSearchKeys.CLIENT_ID_KEY} : {cls.CUSTOMERS_CLIENT_ID}"

    @classmethod
    def get_asset_class_id_facet(cls):
        return f"{FacetSearchKeys.ASSET_CLASS_ID_KEY} : {cls.CUSTOMERS_ASSET_CLASS_ID}"

    @property
    def base_facet_args(self):
        return ' AND '.join([self.get_client_id_facet(), self.get_asset_class_id_facet()])

    def _validate_facets_string(self, facets_string: str):
        facets_string = super()._validate_facets_string(facets_string)
        if self.base_facet_args not in facets_string:
            facets_string += f" AND {self.base_facet_args}"
        return facets_string

    def get_assets(self, facets_string: str, **kwargs) -> Union[list, _Customer]:
        raise DeprecationWarning("use query_for_objects instead")

    def _create_obj(self, response: Response, **kwargs):
        if response:
            return super()._create_obj(response, **kwargs)
        return None

    def _post_req_processing(self, response: Response, **kwargs):
        if self._is_customer_asset(response):
            return super()._post_req_processing(response, **kwargs)
        return None


class WorkOrderSearch(BaseSearch):
    QUERY_URL_ENDPOINT = "workorder/getworkorders"
    DETAILS_URL_ENDPOINT = "workorder?workorderid="
    DEFAULT_ID_TYPE_STR = "WorkOrder"
    RETURNED_OBJ_TYPE = _WorkOrder
    DEFAULT_RESULTS_COUNT_KEY = "WorkOrders"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.query_url = self.base_url + self.__class__.QUERY_URL_ENDPOINT

    def GetWorkOrderDetails(self, **kwargs) -> Optional[_WorkOrder]:
        return self.get_obj_by_id(kwargs.get('workorderid'), **kwargs)

    def QueryWorkOrders(self, facet_string: str = '', **kwargs):
        return self.query_for_objects(facet_string, **kwargs)

    def _print_clean_and_return_query(self, res, print_response=False, **kwargs):
        res = super()._print_clean_and_return_query(res, print_response, **kwargs)

        wo_results = res.json().get(self.results_count_key, None)
        return [self.GetWorkOrderDetails(workorderid=x['ID'])
                for x in wo_results if x is not None]


class AssetClassSearch(BaseSearch):
    DETAILS_URL_ENDPOINT = 'assetclass/details/'  #'assetclass/getassetclassbyid?csid='
    QUERY_URL_ENDPOINT = 'assetclass/getassetclassbyterm?searchterm='

    AC_BY_ACCOUNT_ENDPOINT = 'assetclass/getassetclassbyaccount?accountkey='
    IGNORED_ACCOUNTS = ['ALL_CLIENTS', 'MY_CLIENTS']
    DEFAULT_ID_TYPE_STR = "Asset Class"
    RETURNED_OBJ_TYPE = _AssetClass
    DEFAULT_ERROR_MSG = "ID must be formatted as a GUID."
    DEFAULT_RESULTS_COUNT_KEY = "body"

    def _validate_obj_id_format(self, obj_id, **kwargs):
        if isinstance(obj_id, int):
            pass
        elif obj_id not in self.__class__.IGNORED_ACCOUNTS and not self._isguid(obj_id):
            self._log_and_raise(AttributeError, kwargs.get('err_msg', self.__class__.FULL_DEFAULT_ERROR_MSG))

    # TODO: make sure this isn't redundant
    def get_obj_by_id(self, obj_id=None, **kwargs):
        obj = super().get_obj_by_id(obj_id, **kwargs)
        custom_attrs = {**getattr(obj, 'assetClass'), **{'AssetClassId': obj_id}}
        return _AssetClass(self._logger, **custom_attrs)

    def GetAssetClassDetails(self, **kwargs) -> Optional[_AssetClass]:
        return self.get_obj_by_id(kwargs.get('assetclassid'), **kwargs)

    def _print_clean_and_return_query(self, res, print_response=False, **kwargs):
        res = super()._print_clean_and_return_query(res, print_response, **kwargs)
        ac_results = [x for x in res.json().get(self.results_count_key, None)]
        return [_AssetClass(self._logger, **x)
                for x in ac_results if x is not None]

    def GetAssetClassesByAccount(self, **kwargs):
        self._check_auth()

        payload = {}

        account_id = kwargs.get('accountid', None)
        if not account_id:
            self._get_id_from_input(id_type_str="Account ID")

        print_response = kwargs.get('print_response', False)

        account_url = self.base_url + f'{self.__class__.AC_BY_ACCOUNT_ENDPOINT}{account_id}'

        res = self.ER.make_request("get", account_url, self.base_headers, payload)

        return self._print_clean_and_return_query(res, print_response, results_count_key='body')


class AccountSearch(BaseSearch):
    QUERY_URL_ENDPOINT = "account/getaccountsbysearchterm?searchterm="
    DETAILS_URL_ENDPOINT = "account/getaccounts"
    DEFAULT_ID_TYPE_STR = "Account"
    RETURNED_OBJ_TYPE = _Account
    DEFAULT_ERROR_MSG = "ID must be formatted as a GUID."

    @property
    def details_url(self):
        return self.base_url + self.__class__.DETAILS_URL_ENDPOINT

    def _validate_obj_id_format(self, obj_id, **kwargs):
        if not self._isguid(obj_id):
            self._log_and_raise(AttributeError,
                                kwargs.get('err_msg', self.__class__.FULL_DEFAULT_ERROR_MSG))

    def _create_obj(self, response: Response, **kwargs):
        object_id = kwargs.get('object_id', None)
        if not object_id:
            self._log_and_raise(AttributeError, "object_id must be provided to create an _Account object.")
        return [x for x in self.GetAllAccounts()
                if x.AccountId == object_id][0] if object_id else None

    def _req_obj_by_id(self, obj_id=None, **kwargs) -> Response:
        return None

    def _post_req_processing(self, response: Response, **kwargs):
        print_response = kwargs.get('print_response', False)
        if print_response:
            self._logger.warning("raw response cannot be printed for Account Search")
            print_response = False
        super()._post_req_processing(response, print_response=print_response)

    def get_obj_by_id(self, obj_id=None, **kwargs) -> RETURNED_OBJ_TYPE:
        kwargs['object_id'] = obj_id
        return super().get_obj_by_id(obj_id=obj_id, **kwargs)

    def GetAllAccounts(self):
        self._check_auth()
        payload = {}
        url = self.details_url
        res = self.ER.make_request("GET", url, self.base_headers, payload)

        return [self.__class__.RETURNED_OBJ_TYPE(self._logger, **x) for x in res.json()]


class UserSearch(BaseSearch):
    QUERY_URL_ENDPOINT = "users"
    DETAILS_URL_ENDPOINT = 'user/details?un='
    DEFAULT_ID_TYPE_STR = "User"
    RETURNED_OBJ_TYPE = _User
    DEFAULT_ERROR_MSG = "ID must be formatted as an email address or a GUID."
    DEFAULT_RESULTS_COUNT_KEY = "User"

    @staticmethod
    def _is_email(email):
        return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

    def _validate_obj_id_format(self, obj_id, **kwargs):
        if not self._is_email(obj_id) and not self._isguid(obj_id):
            self._log_and_raise(AttributeError, kwargs.get('err_msg',
                                                           self.__class__.FULL_DEFAULT_ERROR_MSG))

    def _pre_query_checks(self, facets_string: str, **kwargs):
        search_url, return_type, print_response = super()._pre_query_checks(facets_string, **kwargs)
        self._apply_additional_query_params(kwargs)
        return search_url, return_type, print_response

    def _apply_additional_query_params(self, kwargs):
        super()._apply_additional_query_params(kwargs)

        billingAccountId = kwargs.get('billingAccountId', None)
        if not isinstance(billingAccountId, int) or billingAccountId < 1:
            self._log_and_raise(ValueError, "'billingAccountId' must be a positive integer.")
        self.base_query['billingAccountId'] = str(billingAccountId)

    def query_for_objects(self, *args, **kwargs):
        # FIXME: doesn't seem to return anything?
        self._logger.warning("query_for_objects is still in development for UserSearch. "
                             "This simply calls the super() method")
        return super().query_for_objects(*args, **kwargs)
        self._log_and_raise(NotImplementedError, "UserSearch does not support querying for objects YET.")

"""
UtilityCloudAPIWrapper.py

Python wrapper for the utility cloud API

"""
import datetime
# noinspection SpellCheckingInspection
from json import dumps as jdumps
from logging import Logger, getLogger
from configparser import ConfigParser
from typing import Optional, Union, List

# noinspection PyProtectedMember
from UtilityCloudAPIWrapper.Searchers import SearcherFactory, BaseSearch
from UtilityCloudAPIWrapper.initializer import _WrapperInitializer
from UtilityCloudAPIWrapper.Backend import WorkOrderPriority, WorkOrderType, FacetSearchKeys


# noinspection SpellCheckingInspection
class UtilityCloudAPIWrapper(_WrapperInitializer):
    def __init__(self, search_types: Optional[List[Union[str, 'BaseSearch']]] = None, **kwargs):
        self._search_types: List[Union[str, 'BaseSearch']] = []
        self._logger = kwargs.pop('logger', getLogger(__name__))
        super().__init__(logger=self._logger, **kwargs)

        self.search_types = search_types
        self.setup_searchers(**kwargs)

    def _validate_search_type(self, search_type: Union[str, 'BaseSearch']):
        if isinstance(search_type, str):
            return search_type
        elif issubclass(search_type, BaseSearch) and hasattr(search_type, '__name__'):
            return search_type.__name__
        else:
            raise TypeError(f"Invalid search type: {search_type}. "
                            f"Must be a string or a BaseSearch object/subclass with a __name__ attribute.")

    @property
    def search_types(self):
        return self._search_types

    @search_types.setter
    def search_types(self, search_types: Optional[List[Union[str, 'BaseSearch']]]):
        self._search_types = search_types
        if not self._search_types:
            self._search_types = ['ALL']
            self._logger.info("No search types specified. Defaulting to ALL.")
        else:
            for i in self._search_types:
                st = self._validate_search_type(i)
                self._search_types[self._search_types.index(i)] = st

    def setup_searchers(self, **kwargs):
        print_info = kwargs.get('print_info', False)
        print_debug = kwargs.get('print_debug', False)
        if self.search_types[0].lower() == 'all':
            # changed this to a list to make sure search_types is always a list
            self.search_types = [x for x in SearcherFactory.available_types()]
        for search in self.search_types:
            setattr(self, search, SearcherFactory.get_searcher(search_type=search.lower(),
                                                               logger=self._logger, **kwargs))
            self._logger.debug(f"{search} searcher initialized.", print_msg=print_debug)
        self._logger.info(f"{len(self.search_types)} searchers initialized.", print_msg=print_info)


def initialize_uc_wrapper(config=None, logger=None, **kwargs):
    """
    :param config: Configuration object containing base URL for API requests.
    :type config: ConfigParser
    :param logger: Logger object for logging messages.
    :type logger: Logger
    :param kwargs: Additional keyword arguments to be passed to UtilityCloudAPIWrapper initialization.
    :return: Instance of UtilityCloudAPIWrapper initialized with provided configurations.
    :rtype: UtilityCloudAPIWrapper
    """
    if config and config.has_option('DEFAULT', 'base_url'):
        return UtilityCloudAPIWrapper(base_url=config['DEFAULT']['base_url'],
                                      logger=logger, config=config,
                                      use_config=True, auto_auth=True, **kwargs)
    elif config and not config.has_option('DEFAULT', 'base_url'):
        return UtilityCloudAPIWrapper(base_url=UtilityCloudAPIWrapper.BASE_URL_DEFAULT,
                                      logger=logger, config=config, use_config=True,
                                      auto_auth=True, key_dirpath="../Misc_Project_Files", **kwargs)
    else:
        return UtilityCloudAPIWrapper(base_url=UtilityCloudAPIWrapper.BASE_URL_DEFAULT,
                                      logger=logger, config=config, use_config=True,
                                      auto_auth=True, key_dirpath="../Misc_Project_Files", **kwargs)


def get_customer_info_test(searcher: 'AssetSearch'):
    asset_objs = searcher.query_for_objects(facets_string=f"{FacetSearchKeys.DESCRIPTION_KEY} : 189 Colonial",
                                            return_type='id')
    # asset_ids = [273391818]
    for asset in asset_objs:
        print(asset.overview)


if __name__ == '__main__':
    # f'{uc.ASSETTAG_KEY} : 839706865',
    #uc = initialize_uc_wrapper(check_purge=False)
    # from UtilityCloudAPIWrapper.Searchers import SearcherFactory
    # print(SearcherFactory.available_types())
    # exit(-1)

    test_kwargs = {'logger': None, 'config': None, 'use_config': True,
                   'config_filename': 'utility_cloud_api_wrapperConfigAJM.ini',
                   'auto_auth': True, 'key_dirpath': "../Misc_Project_Files"}
    test_search_types = ['WorkOrderSearch', 'AssetSearch']
    uc = UtilityCloudAPIWrapper(print_info=True, base_url=UtilityCloudAPIWrapper.BASE_URL_DEFAULT,
                                **test_kwargs)
    get_customer_info_test(uc.customersubsearcher)
    uc.usersearch.get_obj_by_id('267f26c6-92c3-4392-9b14-34a8af020cfa', print_response=True)#'amcsparron@albanyny.gov', print_response=True)
    uc.usersearch.query_for_objects('Id=267f26c6-92c3-4392-9b14-34a8af020cfa', billingAccountId=316)
    # exit()

    accs = uc.accountsearch.GetAllAccounts()
    ob = uc.accountsearch.get_obj_by_id(obj_id=accs[2].AccountId, print_response=True)
    print(ob.AccountId)
    #exit()

    ac = uc.assetclasssearch.GetAssetClassesByAccount(accountid=accs[2].AccountId)#uc.account_id_dict[-1]['id'])
    print([a.Name for a in ac])
    acd = uc.assetclasssearch.GetAssetClassDetails(assetclassid=ac[2].AssetClassId)
    # assetclassid=55417453
    print(acd.AssetClassId, acd.BillingAccountId)
    #exit()

    emer_priority_id = 1294
    date_created_test = '2020-11-09T19:45:15.87'
    #print(qwo)

    # TODO: this is good for project - QueryWorkOrders to get the date and priority,
    #  then make sure its a WM break with details
    example_facets = 'CREATEDDATE=11/09/2020 AND PRIORITY=1294'  #'Description=Repair water main break #2' TYPE = 1223 AND ASSETCLASS = 55417480 AND CREATEDDATE = 11/09/2020 AND PRIORITY = 1294
    wo_uc = uc.workordersearch
    qwo = wo_uc.QueryWorkOrders(
        facet_string=f'{wo_uc.created_date_equal('11/09/2020')} AND TYPE={WorkOrderType.REPAIR} AND PRIORITY={WorkOrderPriority.EMERGENCY}')
    wod = wo_uc.GetWorkOrderDetails(workorderid=qwo[0].WorkOrderId)  #279989852)
    print(wod)
    date_created_utc = datetime.datetime.fromisoformat(wod.__getattribute__('DateCreated').split('.')[0])
    date_created_est = date_created_utc + datetime.timedelta(hours=-5)

    wm_asset = uc.assetsearch.get_obj_by_id(obj_id=wod.__getattribute__('AssetId'))
    print(wm_asset.FACILITYID)
    # TODO: end of good for project ^^^^^^^^^^^^^^^^^^^^
    also_wm_asset = uc.assetsearch.get_assets(facets_string=f"{FacetSearchKeys.ASSETTAG_KEY}=WM-00071563",
                                               return_type='id')
    print([x.FACILITYID for x in also_wm_asset])

    # uc.check_purge = True
    # uc.purge_all = True
    # defaults to False

    if uc.purge_all:
        uc.PurgeAll()
    elif uc.check_purge:
        uc.PurgeAuthkey()

# workorder ID
# 273391818

# permit asset id - this seems to be for any and all permits?
# 836790301

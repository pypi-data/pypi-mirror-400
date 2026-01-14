import json
from logging import Logger
from ..Backend import AttrPreProcesser


class _Asset(AttrPreProcesser):
    IGNORED_ATTRIBUTES = {'logger', 'available_asset_attributes',
                          'attributes', 'list_attributes_to_preprocess'}
    OVERVIEW_FIELDS = []

    def __init__(self, logger: Logger, **kwargs):
        self.available_asset_attributes = []
        self.logger = logger
        super().__init__(self.logger, kwargs)
        self._load_attributes()

        if not self.__class__.OVERVIEW_FIELDS:
            self.__class__.OVERVIEW_FIELDS = self.available_asset_attributes

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if not hasattr(self, 'IGNORED_ATTRIBUTES') or name not in self.IGNORED_ATTRIBUTES:
            if not hasattr(self, 'available_asset_attributes'):
                self.available_asset_attributes = []
            if name not in self.available_asset_attributes:
                self.available_asset_attributes.append(name)

    def __dir__(self):
        return self.available_asset_attributes

    def __str__(self):
        return f"Asset with AssetID {self.AssetID}"

    @property
    def overview(self):
        return {i: getattr(self, i, 'NO VALUE FOUND') for i in self.__class__.OVERVIEW_FIELDS}

    def _load_attributes(self):
        self.logger.info('loading attributes...')
        for item in self.attributes:
            self.process_attribute(item)
        self.logger.info(f'done loading attributes. '
                         f'{len(self.available_asset_attributes)} '
                         f'asset_attributes loaded.')


class _Customer(_Asset):
    OVERVIEW_FIELDS = ['ClientName', 'Description', 'ClientID',
                       'UCAssetId', 'AssetClassID', 'full_address', 'print_key']

    def __str__(self):
        return str(self.overview)

    def _preprocess_list_item(self, item: dict):
        item = super()._preprocess_list_item(item)
        if item.get('Title', item.get('Key')) == 'full_addre':
            item['Title'] = 'full_address'
        return item


class _WorkOrder(_Asset):
    def __str__(self):
        return f"Work Order with WorkOrderID {self.WorkOrderId}"


class _AssetClass(_Asset):
    def __init__(self, logger: Logger, **kwargs):
        self.list_attributes_to_preprocess = {'AssetClassFields'}
        self.list_attributes_to_preprocess.update(list(self.__class__.DEFAULT_LIST_ATTRS_TO_PREPROCESS))
        super().__init__(logger,
                         list_attributes_to_preprocess=self.list_attributes_to_preprocess,
                         **kwargs)

    @staticmethod
    def _preprocess_asset_class_field(asset_class_field_list: list) -> list:
        processed_list = []
        keys_to_keep = ['FieldTitle', 'AssetClassFieldID']
        for item in asset_class_field_list:
            filtered_field = {key: value for key, value
                              in item.items() if key in keys_to_keep}

            if filtered_field.keys() == set(keys_to_keep):
                processed_list.append(filtered_field)
        return processed_list

    def _process_list_kwarg(self, list_items):
        if len(list_items) == 0:
            self.logger.warning("No attributes were found in the list provided.")
        first_item = list_items[0]
        if 'AssetClassFieldID' in first_item.keys():
            processed_fields = self._preprocess_asset_class_field(list_items)
            setattr(self, 'AssetClassFields', processed_fields)
        else:
            super()._process_list_kwarg(list_items)

    def __str__(self):
        return f"Asset Class with AssetClassID {self.AssetClassId}"


class _Account(_Asset):
    def __str__(self):
        return f"Account with AccountID {self.AccountId}"

    def _preprocess_item(self, old_item):
        new_item = old_item
        if old_item == 'id':
            new_item = 'AccountId'
        return old_item, new_item


class _User(_Asset):
    OVERVIEW_FIELDS = ['UserId', 'LegacyUserId', 'Name', 'JobTitle',
                       'Email', 'PhoneNumber', 'BillingAccountId',
                       'BillingAccountName', 'IsActive']
    IGNORED_ATTRIBUTES = {'User'}
    DEFAULT_LIST_ATTRS_TO_PREPROCESS = {'Phones'}

    def __str__(self):
        return str(self.overview)#f"User with UserId {self.UserId} and LegacyUserId {self.LegacyUserId}"

    def _load_attributes(self):
        self.attributes = {** self.attributes.get('User', {}), ** self.attributes}
        super()._load_attributes()

    @staticmethod
    def _skip_list_item(item):
        if item.get('Number') == '':
            return True
        return False

    def _preprocess_list_item(self, item: dict) -> dict:
        if item.get('Number') and item.get('Number') != '':
            item['Title'] = 'PhoneNumber'
            item['Value'] = item['Number']
        return item

    @property
    def overview(self):
        return {i: getattr(self, i, 'NO VALUE FOUND') for i in self.__class__.OVERVIEW_FIELDS}

    def _preprocess_item(self, old_item):
        new_item = old_item
        if old_item == 'Id':
            new_item = 'UserId'
        elif old_item == 'LegacyId':
            new_item = 'LegacyUserId'
        return old_item, new_item

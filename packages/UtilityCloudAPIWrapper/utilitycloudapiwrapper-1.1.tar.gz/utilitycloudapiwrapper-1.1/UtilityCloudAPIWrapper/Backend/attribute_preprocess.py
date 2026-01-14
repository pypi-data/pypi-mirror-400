class AttrPreProcesser:
    DEFAULT_LIST_ATTRS_TO_PREPROCESS = {'Attributes', 'properties'}

    def __init__(self, logger, attributes: dict, **kwargs):
        self.logger = logger
        self.attributes = attributes
        self.list_attributes_to_preprocess = kwargs.get('list_attributes_to_preprocess',
                                                        self.__class__.DEFAULT_LIST_ATTRS_TO_PREPROCESS)
        self.list_attributes_to_preprocess.update(self.__class__.DEFAULT_LIST_ATTRS_TO_PREPROCESS)

    def _preprocess_list_item(self, item: dict) -> dict:
        if item.get('Title', item.get('Key')) == 'Primary Contact Phone Number':
            item['Title'] = 'PhoneNumber'
            self.logger.debug(f"The attribute \'Primary Contact Phone Number\' was renamed to \'{item['Title']}\'.")
        return item

    def _preprocess_item(self, item):
        return item, item

    @staticmethod
    def _skip_list_item(item):
        return False

    def _process_list_kwarg(self, list_items):
        if len(list_items) == 0:
            self.logger.warning("No attributes were found in the list provided.")
        for item in list_items:
            if self._skip_list_item(item):
                continue
            item = self._preprocess_list_item(item)
            setattr(self, item.get('Title', item.get('Key')), item.get('Value'))

    def _process_list_attribute(self, item: str):
        if item in self.list_attributes_to_preprocess:
            self.logger.debug(f"{item} is a list, processing...")
            self._process_list_kwarg(self.attributes[item])
        else:
            self._process_other_attribute(item)

    def _process_dict_attribute(self, item: str):
        self._process_other_attribute(item)

    def _process_other_attribute(self, item: str):
        old_item, new_item = self._preprocess_item(item)
        setattr(self, new_item, self.attributes[old_item])

    def process_attribute(self, item: str):
        if isinstance(self.attributes[item], list):
            self._process_list_attribute(item)
        # TODO: figure out the best way to parse this...
        elif isinstance(self.attributes[item], dict):
            self._process_dict_attribute(item)
        else:
            self._process_other_attribute(item)
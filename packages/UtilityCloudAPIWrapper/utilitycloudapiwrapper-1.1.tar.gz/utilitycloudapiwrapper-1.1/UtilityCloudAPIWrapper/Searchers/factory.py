from typing import Tuple, Type

from UtilityCloudAPIWrapper.Searchers import BaseSearch


# noinspection PyProtectedMember
class SearcherFactory:
    @staticmethod
    def available_types() -> Tuple[str, ...]:
        """All registered specialized search types (from subclasses that set SEARCH_TYPE)."""
        return tuple(sorted(BaseSearch._REGISTRY.keys()))

    @staticmethod
    def get_searcher(search_type: str,  **kwargs) -> BaseSearch:
        """
        Return an instance of a searcher matching `search_type`.

        - If `search_type` is a registered specialized type, returns that class.
        - Else, raises ValueError.

        Example calls:
            get_searcher('subject')
            get_searcher('attribute', attribute='Body')
        """

        key = (search_type or '').lower().strip()
        # 1) Registered specialized searchers
        if key in BaseSearch._REGISTRY:
            cls: Type[BaseSearch] = BaseSearch._REGISTRY[key]
            return cls(**kwargs)

        raise ValueError(f"Invalid search type: {search_type!r}. "
                         f"Known: {SearcherFactory.available_types()} ")
    # used PyEmailer searcher.BaseSearch and factory as template

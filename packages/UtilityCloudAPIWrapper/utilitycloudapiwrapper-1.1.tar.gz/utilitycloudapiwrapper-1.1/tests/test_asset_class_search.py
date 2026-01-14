import unittest
from unittest.mock import MagicMock

from UtilityCloudAPIWrapper.Searchers import AssetClassSearch


class TestAssetClassSearchValidation(unittest.TestCase):
    def setUp(self):
        self.base_url = "https://example.com/api/"
        self.logger = MagicMock()
        self.search = AssetClassSearch(base_url=self.base_url, logger=self.logger)
        # Pretend we are authenticated to bypass RunAuth
        self.search.auth = "dummy"
        self.search.auth_initialized = True

    def test_isguid_valid_and_invalid(self):
        # Valid GUID
        self.assertTrue(AssetClassSearch._isguid('123e4567-e89b-12d3-a456-426614174000'))
        # Invalid GUID
        self.assertFalse(AssetClassSearch._isguid('not-a-guid'))
        self.assertFalse(AssetClassSearch._isguid('123e4567e89b12d3a456426614174000'))

    def test_validate_obj_id_format_accepts_int_guid_and_ignored(self):
        # Should not raise for int
        self.search._validate_obj_id_format(123)
        # Should not raise for GUID
        self.search._validate_obj_id_format('123e4567-e89b-12d3-a456-426614174000')
        # Should not raise for ignored accounts
        for acc in AssetClassSearch.IGNORED_ACCOUNTS:
            self.search._validate_obj_id_format(acc)

    def test_validate_obj_id_format_raises_for_bad_string(self):
        with self.assertRaises(AttributeError):
            self.search._validate_obj_id_format('bad-string')


if __name__ == '__main__':
    unittest.main()

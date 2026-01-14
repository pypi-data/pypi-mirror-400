import unittest
from unittest.mock import MagicMock

from UtilityCloudAPIWrapper.Searchers import _Asset, _WorkOrder, _AssetClass


class TestReturnObjects(unittest.TestCase):
    def setUp(self):
        self.logger = MagicMock()

    def test_asset_attribute_loading_and_str(self):
        data = {
            'AssetID': 42,
            'Name': 'Main Valve',
            'Attributes': [
                {'Title': 'Primary Contact Phone Number', 'Value': '555-1212'},
                {'Title': 'InstallYear', 'Value': 1991},
            ],
            'properties': [
                {'Key': 'Material', 'Value': 'Ductile Iron'}
            ]
        }
        asset = _Asset(self.logger, **data)
        # PhoneNumber renamed
        self.assertEqual('555-1212', getattr(asset, 'PhoneNumber'))
        # properties Key used for attribute name
        self.assertEqual('Ductile Iron', getattr(asset, 'Material'))
        # available attributes tracking includes set names
        self.assertIn('AssetID', asset.available_asset_attributes)
        self.assertIn('PhoneNumber', asset.available_asset_attributes)
        self.assertIn('InstallYear', asset.available_asset_attributes)
        self.assertIn('Material', asset.available_asset_attributes)
        # __dir__ returns available attributes
        self.assertEqual(sorted(asset.available_asset_attributes), sorted(dir(asset)))
        # __str__ uses assetID
        self.assertIn('Asset with AssetID 42', str(asset))

    def test_workorder_str(self):
        wo = _WorkOrder(self.logger, **{'WorkOrderId': 777, 'Title': 'Leak'})
        self.assertIn('Work Order with WorkOrderID 777', str(wo))

    def test_assetclass_str(self):
        ac = _AssetClass(self.logger, **{'AssetClassId': 555, 'Name': 'Hydrant'})
        self.assertIn('Asset Class with AssetClassID 555', str(ac))


if __name__ == '__main__':
    unittest.main()

# tests\test_UtilityCloudAPIWrapper.py

import unittest
from unittest.mock import patch, MagicMock

from UtilityCloudAPIWrapper import UtilityCloudAPIWrapper
from UtilityCloudAPIWrapper.Searchers import WorkOrderSearch, AssetClassSearch


class TestUtilityCloudAPIWrapper(unittest.TestCase):

    def setUp(self):
        """Set up instances with mock arguments for testing."""
        self.base_url = "https://example.com/api/"
        self.mock_logger = MagicMock()

        # Core wrapper for account and user methods
        self.wrapper = UtilityCloudAPIWrapper(base_url=self.base_url, logger=self.mock_logger)
        self.wrapper.auth = "dummy-auth-token"
        self.wrapper.auth_initialized = True

        # Searchers for work orders and asset classes
        self.wo_search = WorkOrderSearch(base_url=self.base_url, logger=self.mock_logger)
        self.wo_search.auth = "dummy-auth-token"
        self.wo_search.auth_initialized = True

        self.ac_search = AssetClassSearch(base_url=self.base_url, logger=self.mock_logger)
        self.ac_search.auth = "dummy-auth-token"
        self.ac_search.auth_initialized = True

    @patch('UtilityCloudAPIWrapper.Backend.easy_requests.EasyReq.make_request')
    def test_GetWorkOrderDetails(self, mock_make_request):
        """Test the GetWorkOrderDetails method with a valid work order ID."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"work_order": "details"}
        mock_make_request.return_value = mock_response

        result = self.wo_search.GetWorkOrderDetails(workorderid=12345)

        # The searcher returns a _WorkOrder object; here we just ensure the request was made correctly.
        mock_make_request.assert_called_once_with(
            "GET",
            f"{self.base_url}workorder?workorderid=12345",
            self.wo_search.base_headers,
            payload={}
        )

    @patch('UtilityCloudAPIWrapper.Backend.easy_requests.EasyReq.make_request')
    def test_QueryWorkOrders(self, mock_make_request):
        """Test the QueryWorkOrders method with a facet string."""
        mock_response = MagicMock()
        # Return no results to avoid triggering secondary detail calls
        mock_response.json.return_value = {"WorkOrders": []}
        mock_make_request.return_value = mock_response

        result = self.wo_search.QueryWorkOrders(facet_string="CREATEDDATE=2021")

        self.assertEqual([], result)
        mock_make_request.assert_called_once_with(
            "POST",
            f"{self.base_url}workorder/getworkorders",
            headers=self.wo_search.base_headers,
            payload='{"page": 1, "itemCount": "10", "search": "", "SearchFacets": "", "orderby": null, "isAdvanced": true, "filters": null, "isactive": true, "facets": "CREATEDDATE=2021"}'
        )

    @patch('UtilityCloudAPIWrapper.Backend.easy_requests.EasyReq.make_request')
    def test_GetAssetClassByAccount(self, mock_make_request):
        """Test the GetAssetClassesByAccount method with an account ID using AssetClassSearch."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"body": []}
        mock_make_request.return_value = mock_response

        result = self.ac_search.GetAssetClassesByAccount(accountid="123")

        self.assertEqual([], result)
        mock_make_request.assert_called_once_with(
            "get",
            f"{self.base_url}assetclass/getassetclassbyaccount?accountkey=123",
            self.ac_search.base_headers,
            {}
        )


if __name__ == '__main__':
    unittest.main()
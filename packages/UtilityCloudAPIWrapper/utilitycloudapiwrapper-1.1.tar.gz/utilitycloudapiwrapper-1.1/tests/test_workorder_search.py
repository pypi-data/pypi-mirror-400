import unittest
from unittest.mock import MagicMock, patch

from UtilityCloudAPIWrapper.Searchers import WorkOrderSearch, _WorkOrder


class TestWorkOrderSearchFlow(unittest.TestCase):
    def setUp(self):
        self.base_url = "https://example.com/api/"
        self.logger = MagicMock()
        self.search = WorkOrderSearch(base_url=self.base_url, logger=self.logger)
        self.search.auth = "dummy"
        self.search.auth_initialized = True

    @patch('UtilityCloudAPIWrapper.Backend.easy_requests.EasyReq.make_request')
    def test_query_then_fetch_details(self, mock_make_request):
        # First call (POST): return one ID in WorkOrders
        post_resp = MagicMock()
        post_resp.json.return_value = {"WorkOrders": [{"ID": 777}]}
        # Second call (GET details): return details for that work order
        get_resp = MagicMock()
        get_resp.json.return_value = {"WorkOrderId": 777, "Title": "Leak"}
        mock_make_request.side_effect = [post_resp, get_resp]

        result = self.search.QueryWorkOrders(facet_string="PRIORITY=1")

        self.assertIsInstance(result, list)
        self.assertEqual(1, len(result))
        self.assertIsInstance(result[0], _WorkOrder)
        self.assertEqual(777, result[0].WorkOrderId)

        # Ensure POST then GET were called with expected args
        mock_make_request.assert_any_call(
            "POST",
            f"{self.base_url}workorder/getworkorders",
            headers=self.search.base_headers,
            payload='{"page": 1, "itemCount": "10", "search": "", "SearchFacets": "", "orderby": null, "isAdvanced": true, "filters": null, "isactive": true, "facets": "PRIORITY=1"}'
        )
        mock_make_request.assert_any_call(
            "GET",
            f"{self.base_url}workorder?workorderid=777",
            self.search.base_headers,
            payload={}
        )
        self.assertEqual(2, mock_make_request.call_count)


if __name__ == '__main__':
    unittest.main()

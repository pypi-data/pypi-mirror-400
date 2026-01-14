import unittest
from unittest.mock import MagicMock, patch

from UtilityCloudAPIWrapper.Searchers import UserSearch, _User


class TestUserSearch(unittest.TestCase):
    def setUp(self):
        self.base_url = "https://example.com/api/"
        self.logger = MagicMock()
        self.search = UserSearch(base_url=self.base_url, logger=self.logger)
        # Pretend we are authenticated to bypass RunAuth
        self.search.auth = "dummy"
        self.search.auth_initialized = True

    def test_email_and_guid_validation(self):
        # valid email
        self.search._validate_obj_id_format("user@example.com")
        # valid guid
        self.search._validate_obj_id_format('123e4567-e89b-12d3-a456-426614174000')
        # invalid id
        with self.assertRaises(AttributeError):
            self.search._validate_obj_id_format('not-an-id')

    @patch('UtilityCloudAPIWrapper.Backend.easy_requests.EasyReq.make_request')
    def test_billing_account_and_pagination_params_in_post_payload(self, mock_make_request):
        # Mock the POST search response minimal JSON
        post_resp = MagicMock()
        post_resp.json.return_value = {"data": []}
        mock_make_request.return_value = post_resp

        # Execute with additional params
        self.search.query_for_objects(
            "ISACTIVE=1",
            search_url=self.search.query_url,
            billingAccountId=316,
            page=2,
            item_count=25,
            results_count_key='data'
        )

        # Verify POST called once and payload contains our params
        self.assertTrue(mock_make_request.called)
        args, kwargs = mock_make_request.call_args
        # Method and URL
        self.assertEqual("POST", args[0])
        self.assertEqual(self.search.query_url, args[1])
        # Headers present
        self.assertEqual(self.search.base_headers, kwargs['headers'])
        # Ensure payload string contains our additional params (string form for billingAccountId)
        payload = kwargs['payload']
        self.assertIn('"billingAccountId": "316"', payload)
        self.assertIn('"page": 2', payload)
        # item_count stored as string per initializer base_query pattern; BaseSearch uses ItemCount but we only check presence of number
        self.assertIn('25', payload)

    @patch('UtilityCloudAPIWrapper.Backend.easy_requests.EasyReq.make_request')
    def test_get_user_by_email_maps_ids(self, mock_make_request):
        get_resp = MagicMock()
        # API returns Id/LegacyId but _User preprocess remaps to UserId/LegacyUserId
        get_resp.json.return_value = {"Id": "U-1", "LegacyId": 99, "Email": "user@example.com"}
        mock_make_request.return_value = get_resp

        result = self.search.get_obj_by_id(obj_id="user@example.com")
        self.assertIsInstance(result, _User)
        self.assertEqual("U-1", result.UserId)
        self.assertEqual(99, result.LegacyUserId)

    def test_billing_account_validation(self):
        # Negative or non-int should raise from _apply_additional_query_params via pre-checks
        with self.assertRaises(ValueError):
            self.search.query_for_objects("X=1", billingAccountId=0)
        with self.assertRaises(ValueError):
            self.search.query_for_objects("X=1", billingAccountId="abc")


if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import patch, MagicMock

import requests

from UtilityCloudAPIWrapper.Backend import InvalidRequestMethod
from UtilityCloudAPIWrapper.Backend.easy_requests import EasyReq


class TestEasyReq(unittest.TestCase):
    def setUp(self):
        self.logger = MagicMock()

    def _mk_response(self, ok=True, status=200, reason='OK', json_body=None, text=''):
        resp = MagicMock(spec=requests.Response)
        resp.ok = ok
        resp.status_code = status
        resp.reason = reason
        if json_body is not None:
            resp.json.return_value = json_body
        else:
            # Make .json() raise JSONDecodeError if accessed unexpectedly
            resp.json.side_effect = ValueError('No JSON')
        resp.text = text
        return resp

    def test_invalid_method_raises(self):
        er = EasyReq(logger=self.logger)
        with self.assertRaises(InvalidRequestMethod):
            er.make_request('PUT', 'http://example.com', headers={}, payload={})

    @patch('requests.request')
    def test_ok_response_passes_through(self, mock_request):
        er = EasyReq(logger=self.logger)
        mock_request.return_value = self._mk_response(ok=True, status=200, json_body={'x': 1})
        res = er.make_request('GET', 'http://example.com', headers={}, payload=None)
        self.assertTrue(res.ok)
        self.assertEqual(200, res.status_code)
        mock_request.assert_called_once_with('GET', 'http://example.com', headers={}, data=None)

    @patch('requests.request')
    def test_unauthorized_allows_passthrough_when_fail_http_400s_false(self, mock_request):
        er = EasyReq(logger=self.logger, fail_http_400s=False)
        # Simulate a 401 with JSON message
        mock_request.return_value = self._mk_response(ok=False, status=401, reason='Unauthorized', json_body={'message': 'Bad token'})
        res = er.make_request('GET', 'http://example.com', headers={}, payload=None)
        # Should return the raw response (no exception)
        self.assertEqual(401, res.status_code)

    @patch('requests.request')
    def test_too_many_requests_sets_reason_and_raises(self, mock_request):
        er = EasyReq(logger=self.logger)
        mock_request.return_value = self._mk_response(ok=False, status=429, reason='Too Many', json_body={'message': 'Rate limit'})
        with self.assertRaises(requests.RequestException) as ctx:
            er.make_request('GET', 'http://example.com', headers={}, payload=None)
        # The reason should have been replaced by EasyReq
        self.assertIn(EasyReq.TOO_MANY_REQUESTS_REASON, str(ctx.exception))


if __name__ == '__main__':
    unittest.main()

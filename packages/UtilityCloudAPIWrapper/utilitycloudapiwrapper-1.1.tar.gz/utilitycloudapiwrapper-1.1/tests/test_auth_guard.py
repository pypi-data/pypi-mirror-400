import unittest

from UtilityCloudAPIWrapper.Backend import AuthenticationError
from UtilityCloudAPIWrapper.Searchers import WorkOrderSearch


class TestAuthGuard(unittest.TestCase):
    def test_check_auth_raises_when_not_initialized(self):
        # Create without setting auth/auth_initialized to simulate unauthenticated state
        wo = WorkOrderSearch(base_url="https://example.com/api/", logger=None)
        # Directly invoking methods that call _check_auth should raise AuthenticationError
        with self.assertRaises(AuthenticationError):
            wo.QueryWorkOrders(facet_string="ANY=1")
        with self.assertRaises(AuthenticationError):
            wo.GetWorkOrderDetails(workorderid=1)


if __name__ == '__main__':
    unittest.main()

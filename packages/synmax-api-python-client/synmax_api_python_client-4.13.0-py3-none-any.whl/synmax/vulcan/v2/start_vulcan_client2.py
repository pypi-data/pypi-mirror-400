# result = client.transac

# print(result.df())

import os
import unittest
from synmax.vulcan.v2.vulcan_client import VulcanApiClient
import json

class TestVulcanApiMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        api_key = "PSq8zWS3FgHnVGcE2Yz4ZNOBk4SRpUPI"
        x_auth_data = json.dumps({"claims": [{"claim_name":"vulcan_datacenters","claim_json":{"name":"vulcan_datacenters","type":"api","filters":{}}},{"claim_name":"vulcan_underconstruction","claim_json":{"name":"vulcan_underconstruction","type":"api","filters":{}}},{"claim_name":"vulcan_lng_projects","claim_json":{"name":"vulcan_lng_projects","type":"api","filters":{}}},{"claim_name":"vulcan_project_rankings","claim_json":{"name":"vulcan_project_rankings","type":"api","filters":{}}}]})
        cls.client = VulcanApiClient(access_token=api_key)

    def test_all_api_methods(self):
        api_methods = [
            "health",
            "datacenters",
            "underconstruction",
            "lng_projects",
            "project_rankings"
        ]

        for method_name in api_methods:
            with self.subTest(method=method_name):
                print(f"Testing {method_name}...")
                method = getattr(self.client, method_name, None)
                self.assertIsNotNone(method, f"Method '{method_name}' not found on client")

                try:
                    result = method()
                    df = result.df()
                    print(df)
                    self.assertIsNotNone(df, f"{method_name} returned None")
                    self.assertFalse(df.empty, f"{method_name} returned an empty dataframe")
                except Exception as e:
                    self.fail(f"{method_name} raised an exception: {e}")

if __name__ == "__main__":
    unittest.main()

from synmax.leviaton.v1.leviaton_client import LeviatonApiClient


# API Key - Replace with your actual API key
api_key = "36b5ee11-c0c8-4af2-a1d1-ffdd5447597b"

# Initialize the client
client = LeviatonApiClient(access_token=api_key)

# Fetch transactions for USA terminals
# print('starting')
# result = client.transac

# print(result.df())

import os
import unittest
from synmax.leviaton.v1.leviaton_client import LeviatonApiClient
import json

class TestLeviatonApiMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        api_key = "36b5ee11-c0c8-4af2-a1d1-ffdd5447597b"
        # x_auth_data = json.dumps({"claims": [{"claim_name":"leviaton_countries","claim_json":{"name":"leviaton_countries","type":"api","filters":{}}},{"claim_name":"leviaton_terminals","claim_json":{"name":"leviaton_terminals","type":"api","filters":{}}},{"claim_name":"leviaton_transactions","claim_json":{"name":"leviaton_transactions","type":"api","filters":{}}},{"claim_name":"leviaton_vessels","claim_json":{"name":"leviaton_vessels","type":"api","filters":{}}},{"claim_name":"leviaton_volume_flows","claim_json":{"name":"leviaton_volume_flows","type":"api","filters":{}}}]})
        cls.client = LeviatonApiClient(access_token=api_key)

    def test_all_api_methods(self):
        api_methods = [
            "countries",
            "healthcheck",
            "terminals",
            "vessels",
            # "vessels_history",
            "vessels_details",
            "volume_flows",
            "volume_flows/history",
            "transactions",
            "transactions_details",
            "transactions_forecast",
            "transactions_forecast_details",
            "transactions_forecast_history",
            "transactions_forecast_history_details",
            "transactions_history",  
        ]

        for method_name in api_methods:
            with self.subTest(method=method_name):
                print(f"Testing {method_name}...")
                method = getattr(self.client, method_name, None)
                self.assertIsNotNone(method, f"Method '{method_name}' not found on client")

                try:
                    result = method()
                    df = result.df()
                    self.assertIsNotNone(df, f"{method_name} returned None")
                    self.assertFalse(df.empty, f"{method_name} returned an empty dataframe")
                except Exception as e:
                    self.fail(f"{method_name} raised an exception: {e}")

if __name__ == "__main__":
    unittest.main()


# from synmax.leviaton.v1.leviaton_client import LeviatonApiClient

# # API Key - Replace with your actual API key
# api_key = "36b5ee11-c0c8-4af2-a1d1-ffdd5447597b"

# # Initialize the client
# client = LeviatonApiClient(access_token=api_key)

# # Fetch transactions for USA terminals
# result = client.transactions_history(destination_country_codes=["US"])

# # Fetch transactions from specific terminals
# result = client.transactions_history(
#     destination_terminals=["LNG Canada", "Altamira", "Freeport", "Corpus Christi"]
# )

# print(result.df())
from synmax.leviaton.v1.leviaton_client import LeviatonApiClient
import requests
headers={'x-api-key': '36b5ee11-c0c8-4af2-a1d1-ffdd5447597b', "Accept": "application/json"}
key = '36b5ee11-c0c8-4af2-a1d1-ffdd5447597b'
# client = LeviatonApiClient(access_token=headers['x-api-key'])
import json

# claims = {
#     "claims": [
#         {"claim_name": "leviaton_volume_flows", "claim_json": {"name": "leviaton_countries", "type": "api", "filters": {}}},
#         {"claim_name": "leviaton_terminals", "claim_json": {"name": "leviaton_terminals", "type": "api", "filters": {}}},
#         {"claim_name": "leviaton_transactions", "claim_json": {"name": "leviaton_transactions", "type": "api", "filters": {}}},
#         {"claim_name": "leviaton_vessels", "claim_json": {"name": "leviaton_volume_flows", "type": "api", "filters": {}}},
#     ]
# }
# url = f"https://leviaton.api.synmax.com/v1/openapi.yaml"
# url = "http://127.0.0.1:8080/v1/openapi.yaml"
# client = LeviatonApiClient(access_token=key)

# response = requests.get(url, headers=headers, verify=False)
# response.raise_for_status()

# with open(client._spec, "wb") as f:
#     f.write(response.content)
# client._write_stub()

# payload = {
#       "destination_polygons": [
#         [
#             [-125.0, 24.5],
#             [-125.0, 49.5],
#             [-66.9, 49.5],
#             [-66.9, 24.5],
#             [-125.0, 24.5]
#         ],
#         [
#             [122.9, 24.0],
#             [122.9, 45.5],
#             [146.0, 45.5],
#             [146.0, 24.0],
#             [122.9, 24.0]
#         ]
#         ],
#     "from_timestamp": "2025-05-11T12:55:47.957167",
#     "to_timestamp": "2025-05-21T12:55:47.957167",

# }
# results = client.volume_flows_history(transaction_type='loading')
# # results = client.volume_flows(**payload)
# print(results.df())

# res = client.transactions(destination_country_codes=["US"])
# print(res.df())

# for result in results:
#     print(result)

# breakpoint()

# from synmax.leviaton.v1.leviaton_client import LeviatonApiClient

# API Key - Replace with your actual API key
# api_key = "36b5ee11-c0c8-4af2-a1d1-ffdd5447597b"

# Initialize the client
# client = LeviatonApiClient(access_token=key)
# client._write_stub()

# Fetch transactions for USA terminals
# result = client.vessels_history(from_timestamp="2025-01-01T00:00:00Z", to_timestamp="2025-01-22T00:00:00Z")

# Fetch transactions from specific terminals
# result = client.transactions_history(
#     destination_terminals=["LNG Canada", "Altamira", "Freeport", "Corpus Christi"]
# )

# result = client.terminals(countries=["USA"])
# result = client.transactions()
# result = client.vessels()
# result = client.vessels_details()
# result = client.volume_flows_history(transaction_type='loading')
# result = client.volume_flows(transaction_type='loading')
# result = client.countries()
# result = client.transactions_details()
# result = client.transactions_forecast()
# result = client.transactions_forecast_details()
# result = client.transactions_forecast_history()
# result = client.transactions_forecast_history_details()
# result = client.vessels_history()


# print(result.df())for record in result:
#     print(record)
access_token = "eyJwcm9qZWN0X2lkIjogIlN5bm1heCBjb21tZXJjaWFsIEFQSSIsICJwcml2YXRlX2tleSI6ICI5V2lYYUZqdXl1ZkdERXBRSUFhWWd6NG4wZlZLajktVjJocHRaM0RoSWdVIiwgImNsaWVudF9pZCI6ICJzeWRuZWVfZHRpbCIsICJ0eXBlIjogImxvbmdfdGVybV9saWNlbnNlZF9jdXN0b21lciIsICJzdGFydF9kYXRlIjogIjA5LzEyLzIwMjUiLCAiZW5kX2RhdGUiOiAiMTIvMzEvOTk5OSIsICJ0cmlhbF9saWNlbnNlIjogZmFsc2UsICJpc3N1ZV9kYXRldGltZSI6ICIxMi0wOS0yMDI1IDE5OjI5OjQ1IiwgImFkbWluX3VzZXIiOiBmYWxzZSwgInVzZXJfcm9sZXMiOiBbImR0aWxfZXhwYW5zaW9uIiwgImh5cGVyaW9uIiwgInZ1bGNhbiJdfQ=="

from synmax.leviaton.v1 import LeviatonApiClient
leviaton_client = LeviatonApiClient(access_token=access_token)

# Method name:

result =leviaton_client.transactions_history(loading_origin_terminals=["Corpus Christi"], from_timestamp="2025-07-15T22:43:41.371622+00:00", to_timestamp="2025-07-27T22:43:41.371622+00:00")

for record in result:
    print(record)
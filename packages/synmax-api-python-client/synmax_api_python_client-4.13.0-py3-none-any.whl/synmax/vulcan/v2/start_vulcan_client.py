from synmax.vulcan.v2.vulcan_client import VulcanApiClient
import json

VulcanApiClient._write_stub()
# access_token = os.environ.get("ACCESS_TOKEN")

claims_dict = {
    "claims": [
        {"claim_name": "vulcan_datacenters", "claim_json": {"name": "vulcan_datacenters", "type": "api", "filters": {}}},
        {"claim_name": "vulcan_underconstruction", "claim_json": {"name": "vulcan_underconstruction", "type": "api", "filters": {}}},
        {"claim_name": "vulcan_lng_projects", "claim_json": {"name": "vulcan_lng_projects", "type": "api", "filters": {}}},
        {"claim_name": "vulcan_metadata_history", "claim_json": {"name": "vulcan_metadata_history", "type": "api", "filters": {}}},
        {"claim_name": "vulcan_project_rankings", "claim_json": {"name": "vulcan_project_rankings", "type": "api", "filters": {}}},
    ]
}

client = VulcanApiClient(access_token='PSq8zWS3FgHnVGcE2Yz4ZNOBk4SRpUPI')


payload = {}

got = client.lng_projects()
df = got.df()
print(df)

print(got)
breakpoint()
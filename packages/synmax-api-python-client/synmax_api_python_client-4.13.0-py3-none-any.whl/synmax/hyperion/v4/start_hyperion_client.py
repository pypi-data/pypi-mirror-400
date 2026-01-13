# from synmax.hyperion.v4.hyperion_client import HyperionApiClient

# access_token = "eyJwcm9qZWN0X2lkIjogIlN5bm1heCBjb21tZXJjaWFsIEFQSSIsICJwcml2YXRlX2tleSI6ICIwQndzX0ExMFpkdVQyaWlNLS1lbXh3Mk5BNUkxa09kdFNVai04RjVvNzU4IiwgImNsaWVudF9pZCI6ICJGZWxpeCBLZXkiLCAidHlwZSI6ICJvbmVfeWVhcl9saWNlbnNlZF9jdXN0b21lciIsICJzdGFydF9kYXRlIjogIjAzLzE5LzIwMjQiLCAiZW5kX2RhdGUiOiAiMDMvMTkvMjAyNSIsICJ0cmlhbF9saWNlbnNlIjogZmFsc2UsICJpc3N1ZV9kYXRldGltZSI6ICIxOS0wMy0yMDI0IDE0OjI0OjA4IiwgImFkbWluX3VzZXIiOiBmYWxzZSwgInVzZXJfcm9sZXMiOiBbImh5cGVyaW9uIiwgInZ1bGNhbiJdfQ=="

# client = HyperionApiClient(access_token=access_token)

# res = client.wells(response_fields=["county", "date_completion", "date_first_production", "date_permit", "date_spud", "depth_measured", "depth_tvd", "horizontal_length", "lat_bottomhole", "lon_bottomhole", "lat_surface", "lon_surface", "operator", "region_natgas", "state_code", "sub_region_natgas", "well_id", "wellbore_type", "wellpad_id", "produced_formation", "produced_basin"], date_first_production_min="2023-01-31", date_first_production_max="2024-09-01")
# # res = client.daily_production()
# df = res.df()
# print(df)

# from synmax.hyperion.v4 import HyperionApiClient

from synmax.hyperion.v4 import HyperionApiClient

SYNMAX_ACCESS_TOKEN = "eyJwcm9qZWN0X2lkIjogIlN5bm1heCBjb21tZXJjaWFsIEFQSSIsICJwcml2YXRlX2tleSI6ICIwQndzX0ExMFpkdVQyaWlNLS1lbXh3Mk5BNUkxa09kdFNVai04RjVvNzU4IiwgImNsaWVudF9pZCI6ICJGZWxpeCBLZXkiLCAidHlwZSI6ICJvbmVfeWVhcl9saWNlbnNlZF9jdXN0b21lciIsICJzdGFydF9kYXRlIjogIjAzLzE5LzIwMjQiLCAiZW5kX2RhdGUiOiAiMDMvMTkvMjAyNSIsICJ0cmlhbF9saWNlbnNlIjogZmFsc2UsICJpc3N1ZV9kYXRldGltZSI6ICIxOS0wMy0yMDI0IDE0OjI0OjA4IiwgImFkbWluX3VzZXIiOiBmYWxzZSwgInVzZXJfcm9sZXMiOiBbImh5cGVyaW9uIiwgInZ1bGNhbiJdfQ=="
hyperion_api_client = HyperionApiClient(access_token=SYNMAX_ACCESS_TOKEN)

wells_resp = hyperion_api_client.wells(response_fields=["county", "date_completion", "date_first_production", "date_permit", "date_spud", "depth_measured", "depth_tvd", "horizontal_length", "lat_bottomhole", "lon_bottomhole", "lat_surface", "lon_surface", "operator", "region_natgas", "state_code", "sub_region_natgas", "well_id", "wellbore_type", "wellpad_id", "produced_formation", "produced_basin"], date_first_production_min="2023-01-31", date_first_production_max="2024-09-01")

wells_df = wells_resp.df()
wells_df.head()
print(wells_df)
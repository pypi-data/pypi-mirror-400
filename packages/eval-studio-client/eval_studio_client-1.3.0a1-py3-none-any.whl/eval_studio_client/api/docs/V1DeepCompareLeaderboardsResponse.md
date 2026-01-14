# V1DeepCompareLeaderboardsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**leaderboard_cmp_report** | [**V1LeaderboardCmpReport**](V1LeaderboardCmpReport.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_deep_compare_leaderboards_response import V1DeepCompareLeaderboardsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1DeepCompareLeaderboardsResponse from a JSON string
v1_deep_compare_leaderboards_response_instance = V1DeepCompareLeaderboardsResponse.from_json(json)
# print the JSON string representation of the object
print(V1DeepCompareLeaderboardsResponse.to_json())

# convert the object into a dict
v1_deep_compare_leaderboards_response_dict = v1_deep_compare_leaderboards_response_instance.to_dict()
# create an instance of V1DeepCompareLeaderboardsResponse from a dict
v1_deep_compare_leaderboards_response_from_dict = V1DeepCompareLeaderboardsResponse.from_dict(v1_deep_compare_leaderboards_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



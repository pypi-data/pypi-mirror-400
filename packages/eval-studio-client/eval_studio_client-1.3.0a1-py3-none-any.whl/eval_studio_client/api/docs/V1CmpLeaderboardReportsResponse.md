# V1CmpLeaderboardReportsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**leaderboard_cmp_report** | [**V1LeaderboardCmpReport**](V1LeaderboardCmpReport.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_cmp_leaderboard_reports_response import V1CmpLeaderboardReportsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1CmpLeaderboardReportsResponse from a JSON string
v1_cmp_leaderboard_reports_response_instance = V1CmpLeaderboardReportsResponse.from_json(json)
# print the JSON string representation of the object
print(V1CmpLeaderboardReportsResponse.to_json())

# convert the object into a dict
v1_cmp_leaderboard_reports_response_dict = v1_cmp_leaderboard_reports_response_instance.to_dict()
# create an instance of V1CmpLeaderboardReportsResponse from a dict
v1_cmp_leaderboard_reports_response_from_dict = V1CmpLeaderboardReportsResponse.from_dict(v1_cmp_leaderboard_reports_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



# V1LeaderboardCmpReport


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**summary** | **str** | Summary of the comparison. | [optional] 
**comparison_result** | [**V1ComparisonResult**](V1ComparisonResult.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_leaderboard_cmp_report import V1LeaderboardCmpReport

# TODO update the JSON string below
json = "{}"
# create an instance of V1LeaderboardCmpReport from a JSON string
v1_leaderboard_cmp_report_instance = V1LeaderboardCmpReport.from_json(json)
# print the JSON string representation of the object
print(V1LeaderboardCmpReport.to_json())

# convert the object into a dict
v1_leaderboard_cmp_report_dict = v1_leaderboard_cmp_report_instance.to_dict()
# create an instance of V1LeaderboardCmpReport from a dict
v1_leaderboard_cmp_report_from_dict = V1LeaderboardCmpReport.from_dict(v1_leaderboard_cmp_report_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



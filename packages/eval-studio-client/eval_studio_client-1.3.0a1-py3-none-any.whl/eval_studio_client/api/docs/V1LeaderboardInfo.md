# V1LeaderboardInfo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**key** | **str** | Unique key identifying the leaderboard pair (format: \&quot;baseline_id|current_id\&quot;). | [optional] 
**items** | [**List[V1LeaderboardComparisonItem]**](V1LeaderboardComparisonItem.md) | List of leaderboard comparison items. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_leaderboard_info import V1LeaderboardInfo

# TODO update the JSON string below
json = "{}"
# create an instance of V1LeaderboardInfo from a JSON string
v1_leaderboard_info_instance = V1LeaderboardInfo.from_json(json)
# print the JSON string representation of the object
print(V1LeaderboardInfo.to_json())

# convert the object into a dict
v1_leaderboard_info_dict = v1_leaderboard_info_instance.to_dict()
# create an instance of V1LeaderboardInfo from a dict
v1_leaderboard_info_from_dict = V1LeaderboardInfo.from_dict(v1_leaderboard_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



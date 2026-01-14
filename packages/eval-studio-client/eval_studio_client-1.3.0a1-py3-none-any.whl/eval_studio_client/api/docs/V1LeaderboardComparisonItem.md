# V1LeaderboardComparisonItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**wins** | **int** | Number of wins. | [optional] 
**question** | **str** | Question text. | [optional] 
**changed_metrics_count** | **int** | Count of changed metrics. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_leaderboard_comparison_item import V1LeaderboardComparisonItem

# TODO update the JSON string below
json = "{}"
# create an instance of V1LeaderboardComparisonItem from a JSON string
v1_leaderboard_comparison_item_instance = V1LeaderboardComparisonItem.from_json(json)
# print the JSON string representation of the object
print(V1LeaderboardComparisonItem.to_json())

# convert the object into a dict
v1_leaderboard_comparison_item_dict = v1_leaderboard_comparison_item_instance.to_dict()
# create an instance of V1LeaderboardComparisonItem from a dict
v1_leaderboard_comparison_item_from_dict = V1LeaderboardComparisonItem.from_dict(v1_leaderboard_comparison_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



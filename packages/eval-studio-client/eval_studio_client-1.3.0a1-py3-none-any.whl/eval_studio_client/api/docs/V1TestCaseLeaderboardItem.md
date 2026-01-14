# V1TestCaseLeaderboardItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**wins** | **int** | Number of wins. | [optional] 
**question** | **str** | Question text. | [optional] 
**changed_metrics_count** | **int** | Count of changed metrics. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_test_case_leaderboard_item import V1TestCaseLeaderboardItem

# TODO update the JSON string below
json = "{}"
# create an instance of V1TestCaseLeaderboardItem from a JSON string
v1_test_case_leaderboard_item_instance = V1TestCaseLeaderboardItem.from_json(json)
# print the JSON string representation of the object
print(V1TestCaseLeaderboardItem.to_json())

# convert the object into a dict
v1_test_case_leaderboard_item_dict = v1_test_case_leaderboard_item_instance.to_dict()
# create an instance of V1TestCaseLeaderboardItem from a dict
v1_test_case_leaderboard_item_from_dict = V1TestCaseLeaderboardItem.from_dict(v1_test_case_leaderboard_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



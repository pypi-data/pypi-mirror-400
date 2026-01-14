# V1DiffItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**diff_key** | **str** | Unique key identifying the diff (format: \&quot;baseline_id|current_id\&quot;). | [optional] 
**items** | [**List[V1ComparisonItem]**](V1ComparisonItem.md) | List of comparison items. | [optional] 
**summary** | [**V1ComparisonSummary**](V1ComparisonSummary.md) |  | [optional] 
**models_overview** | [**V1ModelsOverview**](V1ModelsOverview.md) |  | [optional] 
**models_comparisons** | [**V1ModelsComparisons**](V1ModelsComparisons.md) |  | [optional] 
**models_comparisons_metrics** | [**V1ModelsComparisonsMetrics**](V1ModelsComparisonsMetrics.md) |  | [optional] 
**technical_metrics** | [**V1TechnicalMetrics**](V1TechnicalMetrics.md) |  | [optional] 
**test_cases_leaderboard** | [**List[V1TestCaseLeaderboardItem]**](V1TestCaseLeaderboardItem.md) | Test cases leaderboard. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_diff_item import V1DiffItem

# TODO update the JSON string below
json = "{}"
# create an instance of V1DiffItem from a JSON string
v1_diff_item_instance = V1DiffItem.from_json(json)
# print the JSON string representation of the object
print(V1DiffItem.to_json())

# convert the object into a dict
v1_diff_item_dict = v1_diff_item_instance.to_dict()
# create an instance of V1DiffItem from a dict
v1_diff_item_from_dict = V1DiffItem.from_dict(v1_diff_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



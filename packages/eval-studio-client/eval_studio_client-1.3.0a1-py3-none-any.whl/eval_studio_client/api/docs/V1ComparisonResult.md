# V1ComparisonResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**diffs** | [**List[V1DiffItem]**](V1DiffItem.md) | List of differences between leaderboards. | [optional] 
**leaderboards** | [**List[V1LeaderboardInfo]**](V1LeaderboardInfo.md) | Leaderboard information. | [optional] 
**metrics_meta** | [**Dict[str, V1MetricMeta]**](V1MetricMeta.md) | Metadata about metrics. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_comparison_result import V1ComparisonResult

# TODO update the JSON string below
json = "{}"
# create an instance of V1ComparisonResult from a JSON string
v1_comparison_result_instance = V1ComparisonResult.from_json(json)
# print the JSON string representation of the object
print(V1ComparisonResult.to_json())

# convert the object into a dict
v1_comparison_result_dict = v1_comparison_result_instance.to_dict()
# create an instance of V1ComparisonResult from a dict
v1_comparison_result_from_dict = V1ComparisonResult.from_dict(v1_comparison_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



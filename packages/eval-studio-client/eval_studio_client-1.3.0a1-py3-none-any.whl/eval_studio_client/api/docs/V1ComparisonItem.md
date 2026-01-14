# V1ComparisonItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**question** | **str** | The question being evaluated. | [optional] 
**diff_flipped_metrics** | [**List[V1FlippedMetric]**](V1FlippedMetric.md) | List of metrics that flipped between baseline and current. | [optional] 
**baseline_test_case_result** | [**V1TestCaseResult**](V1TestCaseResult.md) |  | [optional] 
**baseline_diff_actual_output_meta** | [**V1ActualOutputMetaDiff**](V1ActualOutputMetaDiff.md) |  | [optional] 
**baseline_diff_retrieved_context** | [**V1RetrievedContextDiff**](V1RetrievedContextDiff.md) |  | [optional] 
**current_test_case_result** | [**V1TestCaseResult**](V1TestCaseResult.md) |  | [optional] 
**current_diff_actual_output_meta** | [**V1ActualOutputMetaDiff**](V1ActualOutputMetaDiff.md) |  | [optional] 
**current_diff_retrieved_context** | [**V1RetrievedContextDiff**](V1RetrievedContextDiff.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_comparison_item import V1ComparisonItem

# TODO update the JSON string below
json = "{}"
# create an instance of V1ComparisonItem from a JSON string
v1_comparison_item_instance = V1ComparisonItem.from_json(json)
# print the JSON string representation of the object
print(V1ComparisonItem.to_json())

# convert the object into a dict
v1_comparison_item_dict = v1_comparison_item_instance.to_dict()
# create an instance of V1ComparisonItem from a dict
v1_comparison_item_from_dict = V1ComparisonItem.from_dict(v1_comparison_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



# V1TestCaseResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**key** | **str** | Unique key for the test case. | [optional] 
**input** | **str** | Input text. | [optional] 
**corpus** | **List[str]** | Corpus URLs. | [optional] 
**context** | **List[str]** | Context texts. | [optional] 
**categories** | **List[str]** | Categories. | [optional] 
**relationships** | [**List[V1TestCaseRelationshipInfo]**](V1TestCaseRelationshipInfo.md) | Relationships. | [optional] 
**expected_output** | **str** | Expected output. | [optional] 
**output_constraints** | **List[str]** | Output constraints. | [optional] 
**output_condition** | **str** | Output condition. | [optional] 
**actual_output** | **str** | Actual output generated. | [optional] 
**actual_duration** | **float** | Duration in seconds. | [optional] 
**cost** | **float** | Cost of evaluation. | [optional] 
**model_key** | **str** | Model key. | [optional] 
**test_key** | **str** | Test key. | [optional] 
**test_case_key** | **str** | Test case key. | [optional] 
**metrics** | [**List[V1Metric]**](V1Metric.md) | List of metrics. | [optional] 
**metrics_meta** | **Dict[str, str]** | Metadata for metrics. | [optional] 
**actual_output_meta** | [**List[V1ActualOutputMeta]**](V1ActualOutputMeta.md) | Actual output metadata. | [optional] 
**metric_scores** | [**List[V1ComparisonMetricScore]**](V1ComparisonMetricScore.md) | Metric scores. | [optional] 
**result_error_message** | **str** | Error message if processing resulted in failure. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_test_case_result import V1TestCaseResult

# TODO update the JSON string below
json = "{}"
# create an instance of V1TestCaseResult from a JSON string
v1_test_case_result_instance = V1TestCaseResult.from_json(json)
# print the JSON string representation of the object
print(V1TestCaseResult.to_json())

# convert the object into a dict
v1_test_case_result_dict = v1_test_case_result_instance.to_dict()
# create an instance of V1TestCaseResult from a dict
v1_test_case_result_from_dict = V1TestCaseResult.from_dict(v1_test_case_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



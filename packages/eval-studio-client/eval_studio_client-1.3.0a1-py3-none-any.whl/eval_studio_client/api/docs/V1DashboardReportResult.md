# V1DashboardReportResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**key** | **str** | Output only. Composite unique key of the result formed by the model key and test case key. | [optional] [readonly] 
**input** | **str** | Output only. Input prompt or text to be processed. | [optional] [readonly] 
**expected_output** | **str** | Output only. Expected output or target result. | [optional] [readonly] 
**actual_output** | **str** | Output only. Actual output produced by the model. | [optional] [readonly] 
**model_key** | **str** | Output only. Unique identifier for the model used. | [optional] [readonly] 
**test_case_key** | **str** | Output only. Unique identifier for the test case. | [optional] [readonly] 
**metrics** | [**Dict[str, V1MetricScores]**](V1MetricScores.md) | Optional. All metrics values for the result. Maps evaluator ID to MetricScore. | [optional] 
**result_error_map** | **Dict[str, str]** | Output only. Error message if processing resulted in failure. Maps evaluator ID to error message. | [optional] [readonly] 
**human_decision** | [**V1HumanDecision**](V1HumanDecision.md) |  | [optional] 
**comment** | **str** | Output only. Optional comment about the result. | [optional] [readonly] 
**annotations** | **Dict[str, object]** | Output only. Additional annotations for the result. | [optional] [readonly] 

## Example

```python
from eval_studio_client.api.models.v1_dashboard_report_result import V1DashboardReportResult

# TODO update the JSON string below
json = "{}"
# create an instance of V1DashboardReportResult from a JSON string
v1_dashboard_report_result_instance = V1DashboardReportResult.from_json(json)
# print the JSON string representation of the object
print(V1DashboardReportResult.to_json())

# convert the object into a dict
v1_dashboard_report_result_dict = v1_dashboard_report_result_instance.to_dict()
# create an instance of V1DashboardReportResult from a dict
v1_dashboard_report_result_from_dict = V1DashboardReportResult.from_dict(v1_dashboard_report_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



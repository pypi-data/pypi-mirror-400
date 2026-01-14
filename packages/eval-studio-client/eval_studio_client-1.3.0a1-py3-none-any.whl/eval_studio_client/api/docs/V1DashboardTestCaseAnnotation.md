# V1DashboardTestCaseAnnotation


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] [readonly] 
**create_time** | **datetime** | Output only. Timestamp when the DashboardTestCaseAnnotation was created. | [optional] [readonly] 
**creator** | **str** | Output only. Name of the user or service that requested creation of the DashboardTestCaseAnnotation. | [optional] [readonly] 
**update_time** | **datetime** | Output only. Optional. Timestamp when the DashboardTestCaseAnnotation was last updated. | [optional] [readonly] 
**updater** | **str** | Output only. Optional. Name of the user or service that requested update of the DashboardTestCaseAnnotation. | [optional] [readonly] 
**parent** | **str** | Parent Dashboard Test Case resource name. e.g.: \&quot;dashboards/&lt;UUID&gt;/testCases/&lt;UUID&gt;\&quot;. | [optional] 
**key** | **str** | Immutable. Annotation key. | [optional] 
**value** | **object** | Annotation value. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_dashboard_test_case_annotation import V1DashboardTestCaseAnnotation

# TODO update the JSON string below
json = "{}"
# create an instance of V1DashboardTestCaseAnnotation from a JSON string
v1_dashboard_test_case_annotation_instance = V1DashboardTestCaseAnnotation.from_json(json)
# print the JSON string representation of the object
print(V1DashboardTestCaseAnnotation.to_json())

# convert the object into a dict
v1_dashboard_test_case_annotation_dict = v1_dashboard_test_case_annotation_instance.to_dict()
# create an instance of V1DashboardTestCaseAnnotation from a dict
v1_dashboard_test_case_annotation_from_dict = V1DashboardTestCaseAnnotation.from_dict(v1_dashboard_test_case_annotation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



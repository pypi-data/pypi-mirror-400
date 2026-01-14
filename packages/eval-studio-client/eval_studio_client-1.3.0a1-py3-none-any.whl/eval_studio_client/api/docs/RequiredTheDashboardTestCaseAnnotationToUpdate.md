# RequiredTheDashboardTestCaseAnnotationToUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**create_time** | **datetime** | Output only. Timestamp when the DashboardTestCaseAnnotation was created. | [optional] [readonly] 
**creator** | **str** | Output only. Name of the user or service that requested creation of the DashboardTestCaseAnnotation. | [optional] [readonly] 
**update_time** | **datetime** | Output only. Optional. Timestamp when the DashboardTestCaseAnnotation was last updated. | [optional] [readonly] 
**updater** | **str** | Output only. Optional. Name of the user or service that requested update of the DashboardTestCaseAnnotation. | [optional] [readonly] 
**parent** | **str** | Parent Dashboard Test Case resource name. e.g.: \&quot;dashboards/&lt;UUID&gt;/testCases/&lt;UUID&gt;\&quot;. | [optional] 
**key** | **str** | Immutable. Annotation key. | [optional] 
**value** | **object** | Annotation value. | [optional] 

## Example

```python
from eval_studio_client.api.models.required_the_dashboard_test_case_annotation_to_update import RequiredTheDashboardTestCaseAnnotationToUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of RequiredTheDashboardTestCaseAnnotationToUpdate from a JSON string
required_the_dashboard_test_case_annotation_to_update_instance = RequiredTheDashboardTestCaseAnnotationToUpdate.from_json(json)
# print the JSON string representation of the object
print(RequiredTheDashboardTestCaseAnnotationToUpdate.to_json())

# convert the object into a dict
required_the_dashboard_test_case_annotation_to_update_dict = required_the_dashboard_test_case_annotation_to_update_instance.to_dict()
# create an instance of RequiredTheDashboardTestCaseAnnotationToUpdate from a dict
required_the_dashboard_test_case_annotation_to_update_from_dict = RequiredTheDashboardTestCaseAnnotationToUpdate.from_dict(required_the_dashboard_test_case_annotation_to_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



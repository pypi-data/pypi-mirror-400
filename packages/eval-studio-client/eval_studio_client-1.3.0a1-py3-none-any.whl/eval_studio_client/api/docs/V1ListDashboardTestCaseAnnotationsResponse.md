# V1ListDashboardTestCaseAnnotationsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dashboard_test_case_annotations** | [**List[V1DashboardTestCaseAnnotation]**](V1DashboardTestCaseAnnotation.md) | The list of DashboardTestCaseAnnotations. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_list_dashboard_test_case_annotations_response import V1ListDashboardTestCaseAnnotationsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListDashboardTestCaseAnnotationsResponse from a JSON string
v1_list_dashboard_test_case_annotations_response_instance = V1ListDashboardTestCaseAnnotationsResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListDashboardTestCaseAnnotationsResponse.to_json())

# convert the object into a dict
v1_list_dashboard_test_case_annotations_response_dict = v1_list_dashboard_test_case_annotations_response_instance.to_dict()
# create an instance of V1ListDashboardTestCaseAnnotationsResponse from a dict
v1_list_dashboard_test_case_annotations_response_from_dict = V1ListDashboardTestCaseAnnotationsResponse.from_dict(v1_list_dashboard_test_case_annotations_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



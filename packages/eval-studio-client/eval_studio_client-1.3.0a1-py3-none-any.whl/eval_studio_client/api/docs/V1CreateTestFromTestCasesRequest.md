# V1CreateTestFromTestCasesRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tests_json** | **str** | Test Cases in JSON format. | [optional] 
**url** | **str** | URL pointing to the Test Cases in JSON format to import. | [optional] 
**test_display_name** | **str** | Required. Display name of the newly created Test. | [optional] 
**test_description** | **str** | Optional. Description of the newly created Tests. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_create_test_from_test_cases_request import V1CreateTestFromTestCasesRequest

# TODO update the JSON string below
json = "{}"
# create an instance of V1CreateTestFromTestCasesRequest from a JSON string
v1_create_test_from_test_cases_request_instance = V1CreateTestFromTestCasesRequest.from_json(json)
# print the JSON string representation of the object
print(V1CreateTestFromTestCasesRequest.to_json())

# convert the object into a dict
v1_create_test_from_test_cases_request_dict = v1_create_test_from_test_cases_request_instance.to_dict()
# create an instance of V1CreateTestFromTestCasesRequest from a dict
v1_create_test_from_test_cases_request_from_dict = V1CreateTestFromTestCasesRequest.from_dict(v1_create_test_from_test_cases_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



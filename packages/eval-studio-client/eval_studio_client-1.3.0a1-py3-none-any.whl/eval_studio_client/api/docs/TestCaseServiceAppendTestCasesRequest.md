# TestCaseServiceAppendTestCasesRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**test_cases_json** | **str** | Test Cases in JSON format. | [optional] 
**url** | **str** | URL pointing to the Test Cases in JSON format to import. | [optional] 

## Example

```python
from eval_studio_client.api.models.test_case_service_append_test_cases_request import TestCaseServiceAppendTestCasesRequest

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseServiceAppendTestCasesRequest from a JSON string
test_case_service_append_test_cases_request_instance = TestCaseServiceAppendTestCasesRequest.from_json(json)
# print the JSON string representation of the object
print(TestCaseServiceAppendTestCasesRequest.to_json())

# convert the object into a dict
test_case_service_append_test_cases_request_dict = test_case_service_append_test_cases_request_instance.to_dict()
# create an instance of TestCaseServiceAppendTestCasesRequest from a dict
test_case_service_append_test_cases_request_from_dict = TestCaseServiceAppendTestCasesRequest.from_dict(test_case_service_append_test_cases_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



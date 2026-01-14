# V1TestCaseRelationshipInfo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** | Type of the relationship. | [optional] 
**target** | **str** | Target of the relationship. | [optional] 
**target_type** | **str** | Type of the target. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_test_case_relationship_info import V1TestCaseRelationshipInfo

# TODO update the JSON string below
json = "{}"
# create an instance of V1TestCaseRelationshipInfo from a JSON string
v1_test_case_relationship_info_instance = V1TestCaseRelationshipInfo.from_json(json)
# print the JSON string representation of the object
print(V1TestCaseRelationshipInfo.to_json())

# convert the object into a dict
v1_test_case_relationship_info_dict = v1_test_case_relationship_info_instance.to_dict()
# create an instance of V1TestCaseRelationshipInfo from a dict
v1_test_case_relationship_info_from_dict = V1TestCaseRelationshipInfo.from_dict(v1_test_case_relationship_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



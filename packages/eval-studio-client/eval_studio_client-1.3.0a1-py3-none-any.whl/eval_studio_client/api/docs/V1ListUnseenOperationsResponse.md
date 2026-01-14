# V1ListUnseenOperationsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**operations** | [**List[V1Operation]**](V1Operation.md) | The list of Operations that the user has not seen. | [optional] 
**total_size** | **int** | The total number of unseen Operations that match the request, irrespective of pagination. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_list_unseen_operations_response import V1ListUnseenOperationsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListUnseenOperationsResponse from a JSON string
v1_list_unseen_operations_response_instance = V1ListUnseenOperationsResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListUnseenOperationsResponse.to_json())

# convert the object into a dict
v1_list_unseen_operations_response_dict = v1_list_unseen_operations_response_instance.to_dict()
# create an instance of V1ListUnseenOperationsResponse from a dict
v1_list_unseen_operations_response_from_dict = V1ListUnseenOperationsResponse.from_dict(v1_list_unseen_operations_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



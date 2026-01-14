# V1BatchMarkOperationSeenByCreatorResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**operations** | [**List[V1Operation]**](V1Operation.md) | The updated Operations. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_batch_mark_operation_seen_by_creator_response import V1BatchMarkOperationSeenByCreatorResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1BatchMarkOperationSeenByCreatorResponse from a JSON string
v1_batch_mark_operation_seen_by_creator_response_instance = V1BatchMarkOperationSeenByCreatorResponse.from_json(json)
# print the JSON string representation of the object
print(V1BatchMarkOperationSeenByCreatorResponse.to_json())

# convert the object into a dict
v1_batch_mark_operation_seen_by_creator_response_dict = v1_batch_mark_operation_seen_by_creator_response_instance.to_dict()
# create an instance of V1BatchMarkOperationSeenByCreatorResponse from a dict
v1_batch_mark_operation_seen_by_creator_response_from_dict = V1BatchMarkOperationSeenByCreatorResponse.from_dict(v1_batch_mark_operation_seen_by_creator_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



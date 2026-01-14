# V1MarkOperationSeenByCreatorResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**operation** | [**V1Operation**](V1Operation.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_mark_operation_seen_by_creator_response import V1MarkOperationSeenByCreatorResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1MarkOperationSeenByCreatorResponse from a JSON string
v1_mark_operation_seen_by_creator_response_instance = V1MarkOperationSeenByCreatorResponse.from_json(json)
# print the JSON string representation of the object
print(V1MarkOperationSeenByCreatorResponse.to_json())

# convert the object into a dict
v1_mark_operation_seen_by_creator_response_dict = v1_mark_operation_seen_by_creator_response_instance.to_dict()
# create an instance of V1MarkOperationSeenByCreatorResponse from a dict
v1_mark_operation_seen_by_creator_response_from_dict = V1MarkOperationSeenByCreatorResponse.from_dict(v1_mark_operation_seen_by_creator_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



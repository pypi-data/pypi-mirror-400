# V1ActualOutputMeta


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tokenization** | **str** | Tokenization method. | [optional] 
**data** | [**List[V1DataFragment]**](V1DataFragment.md) | Data fragments. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_actual_output_meta import V1ActualOutputMeta

# TODO update the JSON string below
json = "{}"
# create an instance of V1ActualOutputMeta from a JSON string
v1_actual_output_meta_instance = V1ActualOutputMeta.from_json(json)
# print the JSON string representation of the object
print(V1ActualOutputMeta.to_json())

# convert the object into a dict
v1_actual_output_meta_dict = v1_actual_output_meta_instance.to_dict()
# create an instance of V1ActualOutputMeta from a dict
v1_actual_output_meta_from_dict = V1ActualOutputMeta.from_dict(v1_actual_output_meta_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



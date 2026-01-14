# V1DataFragment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**text** | **str** | Text content. | [optional] 
**metrics** | **Dict[str, float]** | Metrics for this fragment. | [optional] 
**meta** | **Dict[str, str]** | Additional metadata. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_data_fragment import V1DataFragment

# TODO update the JSON string below
json = "{}"
# create an instance of V1DataFragment from a JSON string
v1_data_fragment_instance = V1DataFragment.from_json(json)
# print the JSON string representation of the object
print(V1DataFragment.to_json())

# convert the object into a dict
v1_data_fragment_dict = v1_data_fragment_instance.to_dict()
# create an instance of V1DataFragment from a dict
v1_data_fragment_from_dict = V1DataFragment.from_dict(v1_data_fragment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



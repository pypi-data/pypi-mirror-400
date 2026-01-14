# V1ModelsOverview


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**baseline_model_key** | **str** | Baseline model key. | [optional] 
**current_model_key** | **str** | Current model key. | [optional] 
**baseline_model_name** | **str** | Baseline model name. | [optional] 
**baseline_collection_id** | **List[str]** | Baseline collection IDs. | [optional] 
**current_model_name** | **str** | Current model name. | [optional] 
**current_collection_id** | **List[str]** | Current collection IDs. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_models_overview import V1ModelsOverview

# TODO update the JSON string below
json = "{}"
# create an instance of V1ModelsOverview from a JSON string
v1_models_overview_instance = V1ModelsOverview.from_json(json)
# print the JSON string representation of the object
print(V1ModelsOverview.to_json())

# convert the object into a dict
v1_models_overview_dict = v1_models_overview_instance.to_dict()
# create an instance of V1ModelsOverview from a dict
v1_models_overview_from_dict = V1ModelsOverview.from_dict(v1_models_overview_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



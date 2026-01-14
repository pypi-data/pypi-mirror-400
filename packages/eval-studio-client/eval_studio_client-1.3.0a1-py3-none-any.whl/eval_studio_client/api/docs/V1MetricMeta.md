# V1MetricMeta


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**key** | **str** | Metric key. | [optional] 
**display_name** | **str** | Display name. | [optional] 
**data_type** | **str** | Data type. | [optional] 
**display_value** | **str** | Display value format. | [optional] 
**description** | **str** | Description. | [optional] 
**value_range** | **List[float]** | Value range (min, max). | [optional] 
**value_enum** | **List[str]** | Value enum (null if not applicable). | [optional] 
**higher_is_better** | **bool** | Whether higher is better. | [optional] 
**threshold** | **float** | Threshold value. | [optional] 
**is_primary_metric** | **bool** | Is primary metric. | [optional] 
**parent_metric** | **str** | Parent metric. | [optional] 
**exclude** | **bool** | Exclude flag. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_metric_meta import V1MetricMeta

# TODO update the JSON string below
json = "{}"
# create an instance of V1MetricMeta from a JSON string
v1_metric_meta_instance = V1MetricMeta.from_json(json)
# print the JSON string representation of the object
print(V1MetricMeta.to_json())

# convert the object into a dict
v1_metric_meta_dict = v1_metric_meta_instance.to_dict()
# create an instance of V1MetricMeta from a dict
v1_metric_meta_from_dict = V1MetricMeta.from_dict(v1_metric_meta_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



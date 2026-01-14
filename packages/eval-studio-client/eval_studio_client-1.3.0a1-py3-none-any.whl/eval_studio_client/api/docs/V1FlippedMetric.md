# V1FlippedMetric


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**metric_name** | **str** | Metric name. | [optional] 
**baseline_value** | **float** | Baseline value. | [optional] 
**current_value** | **float** | Current value. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_flipped_metric import V1FlippedMetric

# TODO update the JSON string below
json = "{}"
# create an instance of V1FlippedMetric from a JSON string
v1_flipped_metric_instance = V1FlippedMetric.from_json(json)
# print the JSON string representation of the object
print(V1FlippedMetric.to_json())

# convert the object into a dict
v1_flipped_metric_dict = v1_flipped_metric_instance.to_dict()
# create an instance of V1FlippedMetric from a dict
v1_flipped_metric_from_dict = V1FlippedMetric.from_dict(v1_flipped_metric_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



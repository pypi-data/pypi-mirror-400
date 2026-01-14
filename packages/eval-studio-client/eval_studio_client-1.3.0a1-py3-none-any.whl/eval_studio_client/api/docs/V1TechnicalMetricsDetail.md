# V1TechnicalMetricsDetail


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cost_sum** | **float** | Sum of costs. | [optional] 
**duration_sum** | **float** | Sum of durations. | [optional] 
**duration_min** | **float** | Minimum duration. | [optional] 
**duration_max** | **float** | Maximum duration. | [optional] 
**duration_avg** | **float** | Average duration. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_technical_metrics_detail import V1TechnicalMetricsDetail

# TODO update the JSON string below
json = "{}"
# create an instance of V1TechnicalMetricsDetail from a JSON string
v1_technical_metrics_detail_instance = V1TechnicalMetricsDetail.from_json(json)
# print the JSON string representation of the object
print(V1TechnicalMetricsDetail.to_json())

# convert the object into a dict
v1_technical_metrics_detail_dict = v1_technical_metrics_detail_instance.to_dict()
# create an instance of V1TechnicalMetricsDetail from a dict
v1_technical_metrics_detail_from_dict = V1TechnicalMetricsDetail.from_dict(v1_technical_metrics_detail_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



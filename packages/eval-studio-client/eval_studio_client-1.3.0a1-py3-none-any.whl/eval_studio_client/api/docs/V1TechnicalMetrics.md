# V1TechnicalMetrics


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**baseline** | [**V1TechnicalMetricsDetail**](V1TechnicalMetricsDetail.md) |  | [optional] 
**current** | [**V1TechnicalMetricsDetail**](V1TechnicalMetricsDetail.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_technical_metrics import V1TechnicalMetrics

# TODO update the JSON string below
json = "{}"
# create an instance of V1TechnicalMetrics from a JSON string
v1_technical_metrics_instance = V1TechnicalMetrics.from_json(json)
# print the JSON string representation of the object
print(V1TechnicalMetrics.to_json())

# convert the object into a dict
v1_technical_metrics_dict = v1_technical_metrics_instance.to_dict()
# create an instance of V1TechnicalMetrics from a dict
v1_technical_metrics_from_dict = V1TechnicalMetrics.from_dict(v1_technical_metrics_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



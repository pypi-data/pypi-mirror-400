# V1MetricAverage


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**metric_key** | **str** | Metric key. | [optional] 
**baseline_avg** | **float** | Baseline average. | [optional] 
**current_avg** | **float** | Current average. | [optional] 
**diff** | **float** | Difference between current and baseline. | [optional] 
**baseline_better_wins** | **int** | Baseline better wins count. | [optional] 
**current_better_wins** | **int** | Current better wins count. | [optional] 
**baseline_rank_avg** | **float** | Baseline rank average. | [optional] 
**current_rank_avg** | **float** | Current rank average. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_metric_average import V1MetricAverage

# TODO update the JSON string below
json = "{}"
# create an instance of V1MetricAverage from a JSON string
v1_metric_average_instance = V1MetricAverage.from_json(json)
# print the JSON string representation of the object
print(V1MetricAverage.to_json())

# convert the object into a dict
v1_metric_average_dict = v1_metric_average_instance.to_dict()
# create an instance of V1MetricAverage from a dict
v1_metric_average_from_dict = V1MetricAverage.from_dict(v1_metric_average_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



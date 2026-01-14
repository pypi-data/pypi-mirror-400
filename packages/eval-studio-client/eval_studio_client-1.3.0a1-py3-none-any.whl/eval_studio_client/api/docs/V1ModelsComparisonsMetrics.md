# V1ModelsComparisonsMetrics


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**metrics_ranks_baseline** | **float** | Metrics ranks for baseline. | [optional] 
**metrics_ranks_current** | **float** | Metrics ranks for current. | [optional] 
**metrics_wins_baseline** | **int** | Metrics wins for baseline. | [optional] 
**metrics_wins_current** | **int** | Metrics wins for current. | [optional] 
**metrics_averages** | [**List[V1MetricAverage]**](V1MetricAverage.md) | Metrics averages. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_models_comparisons_metrics import V1ModelsComparisonsMetrics

# TODO update the JSON string below
json = "{}"
# create an instance of V1ModelsComparisonsMetrics from a JSON string
v1_models_comparisons_metrics_instance = V1ModelsComparisonsMetrics.from_json(json)
# print the JSON string representation of the object
print(V1ModelsComparisonsMetrics.to_json())

# convert the object into a dict
v1_models_comparisons_metrics_dict = v1_models_comparisons_metrics_instance.to_dict()
# create an instance of V1ModelsComparisonsMetrics from a dict
v1_models_comparisons_metrics_from_dict = V1ModelsComparisonsMetrics.from_dict(v1_models_comparisons_metrics_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



# V1ComparisonMetricScore


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**metric_name** | **str** | Metric name. | [optional] 
**metric_score** | **float** | Metric score value. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_comparison_metric_score import V1ComparisonMetricScore

# TODO update the JSON string below
json = "{}"
# create an instance of V1ComparisonMetricScore from a JSON string
v1_comparison_metric_score_instance = V1ComparisonMetricScore.from_json(json)
# print the JSON string representation of the object
print(V1ComparisonMetricScore.to_json())

# convert the object into a dict
v1_comparison_metric_score_dict = v1_comparison_metric_score_instance.to_dict()
# create an instance of V1ComparisonMetricScore from a dict
v1_comparison_metric_score_from_dict = V1ComparisonMetricScore.from_dict(v1_comparison_metric_score_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



# V1AllMetricScores


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**scores** | **List[float]** | Required. Metric scores for all baseline test cases. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_all_metric_scores import V1AllMetricScores

# TODO update the JSON string below
json = "{}"
# create an instance of V1AllMetricScores from a JSON string
v1_all_metric_scores_instance = V1AllMetricScores.from_json(json)
# print the JSON string representation of the object
print(V1AllMetricScores.to_json())

# convert the object into a dict
v1_all_metric_scores_dict = v1_all_metric_scores_instance.to_dict()
# create an instance of V1AllMetricScores from a dict
v1_all_metric_scores_from_dict = V1AllMetricScores.from_dict(v1_all_metric_scores_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



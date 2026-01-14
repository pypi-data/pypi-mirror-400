# V1ComparisonSummary


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**recommendation_winner** | **str** | Winner of the comparison (baseline, current, or tie). | [optional] 
**recommendation** | **str** | Recommendation text. | [optional] 
**recommendation_confidence** | **str** | Confidence level of the recommendation. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_comparison_summary import V1ComparisonSummary

# TODO update the JSON string below
json = "{}"
# create an instance of V1ComparisonSummary from a JSON string
v1_comparison_summary_instance = V1ComparisonSummary.from_json(json)
# print the JSON string representation of the object
print(V1ComparisonSummary.to_json())

# convert the object into a dict
v1_comparison_summary_dict = v1_comparison_summary_instance.to_dict()
# create an instance of V1ComparisonSummary from a dict
v1_comparison_summary_from_dict = V1ComparisonSummary.from_dict(v1_comparison_summary_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



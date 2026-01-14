# V1ModelsComparisons


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**test_case_ranks_baseline** | **int** | Test case ranks for baseline. | [optional] 
**test_case_ranks_current** | **int** | Test case ranks for current. | [optional] 
**test_case_wins_baseline** | **int** | Test case wins for baseline. | [optional] 
**test_case_wins_current** | **int** | Test case wins for current. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_models_comparisons import V1ModelsComparisons

# TODO update the JSON string below
json = "{}"
# create an instance of V1ModelsComparisons from a JSON string
v1_models_comparisons_instance = V1ModelsComparisons.from_json(json)
# print the JSON string representation of the object
print(V1ModelsComparisons.to_json())

# convert the object into a dict
v1_models_comparisons_dict = v1_models_comparisons_instance.to_dict()
# create an instance of V1ModelsComparisons from a dict
v1_models_comparisons_from_dict = V1ModelsComparisons.from_dict(v1_models_comparisons_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



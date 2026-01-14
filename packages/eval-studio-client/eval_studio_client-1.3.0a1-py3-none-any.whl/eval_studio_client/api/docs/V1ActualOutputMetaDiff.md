# V1ActualOutputMetaDiff


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sentences** | **List[str]** | Sentences. | [optional] 
**sentences_count** | **int** | Sentence count. | [optional] 
**common_sentences** | **List[str]** | Common sentences between baseline and current. | [optional] 
**common_count** | **int** | Common sentence count. | [optional] 
**unique_sentences** | **List[str]** | Unique sentences. | [optional] 
**unique_count** | **int** | Unique sentence count. | [optional] 
**identical** | **bool** | Whether outputs are identical. | [optional] 
**sentence_similarity** | **Dict[str, float]** | Sentence similarity scores. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_actual_output_meta_diff import V1ActualOutputMetaDiff

# TODO update the JSON string below
json = "{}"
# create an instance of V1ActualOutputMetaDiff from a JSON string
v1_actual_output_meta_diff_instance = V1ActualOutputMetaDiff.from_json(json)
# print the JSON string representation of the object
print(V1ActualOutputMetaDiff.to_json())

# convert the object into a dict
v1_actual_output_meta_diff_dict = v1_actual_output_meta_diff_instance.to_dict()
# create an instance of V1ActualOutputMetaDiff from a dict
v1_actual_output_meta_diff_from_dict = V1ActualOutputMetaDiff.from_dict(v1_actual_output_meta_diff_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



# V1RetrievedContextDiff


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**chunks** | **List[str]** | Context chunks. | [optional] 
**chunks_count** | **int** | Chunk count. | [optional] 
**common_chunks** | **List[str]** | Common chunks between baseline and current. | [optional] 
**common_count** | **int** | Common chunk count. | [optional] 
**unique_chunks** | **List[str]** | Unique chunks. | [optional] 
**unique_count** | **int** | Unique chunk count. | [optional] 
**identical** | **bool** | Whether contexts are identical. | [optional] 
**chunk_similarity** | **Dict[str, float]** | Chunk similarity scores. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_retrieved_context_diff import V1RetrievedContextDiff

# TODO update the JSON string below
json = "{}"
# create an instance of V1RetrievedContextDiff from a JSON string
v1_retrieved_context_diff_instance = V1RetrievedContextDiff.from_json(json)
# print the JSON string representation of the object
print(V1RetrievedContextDiff.to_json())

# convert the object into a dict
v1_retrieved_context_diff_dict = v1_retrieved_context_diff_instance.to_dict()
# create an instance of V1RetrievedContextDiff from a dict
v1_retrieved_context_diff_from_dict = V1RetrievedContextDiff.from_dict(v1_retrieved_context_diff_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



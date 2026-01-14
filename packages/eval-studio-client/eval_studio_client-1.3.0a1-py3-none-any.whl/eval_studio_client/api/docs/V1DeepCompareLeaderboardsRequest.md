# V1DeepCompareLeaderboardsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**leaderboard_baseline_name** | **str** | Required. The resource name of the baseline leaderboard to compare against. | [optional] 
**leaderboard_current_name** | **str** | Required. The resource name of the current leaderboard to compare. | [optional] 
**text_similarity_metric** | [**V1TextSimilarityMetric**](V1TextSimilarityMetric.md) |  | [optional] 
**llm_model_baseline_name** | **str** | Required. The baseline LLM model name to compare. | [optional] 
**llm_model_current_name** | **str** | Required. The current LLM model name to compare. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_deep_compare_leaderboards_request import V1DeepCompareLeaderboardsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of V1DeepCompareLeaderboardsRequest from a JSON string
v1_deep_compare_leaderboards_request_instance = V1DeepCompareLeaderboardsRequest.from_json(json)
# print the JSON string representation of the object
print(V1DeepCompareLeaderboardsRequest.to_json())

# convert the object into a dict
v1_deep_compare_leaderboards_request_dict = v1_deep_compare_leaderboards_request_instance.to_dict()
# create an instance of V1DeepCompareLeaderboardsRequest from a dict
v1_deep_compare_leaderboards_request_from_dict = V1DeepCompareLeaderboardsRequest.from_dict(v1_deep_compare_leaderboards_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



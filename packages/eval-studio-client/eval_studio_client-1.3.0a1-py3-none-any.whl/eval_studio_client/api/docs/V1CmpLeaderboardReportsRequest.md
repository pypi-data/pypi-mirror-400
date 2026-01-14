# V1CmpLeaderboardReportsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**leaderboard_report_baseline** | **str** | Required. The baseline Leaderboard Report to compare against (JSON string). | [optional] 
**leaderboard_report_current** | **str** | Required. The current Leaderboard Report to compare (JSON string). | [optional] 
**text_similarity_metric** | [**V1TextSimilarityMetric**](V1TextSimilarityMetric.md) |  | [optional] 
**llm_model_name_baseline** | **str** | Required. The baseline LLM model name to compare. | [optional] 
**llm_model_name_current** | **str** | Required. The current LLM model name to compare. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_cmp_leaderboard_reports_request import V1CmpLeaderboardReportsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of V1CmpLeaderboardReportsRequest from a JSON string
v1_cmp_leaderboard_reports_request_instance = V1CmpLeaderboardReportsRequest.from_json(json)
# print the JSON string representation of the object
print(V1CmpLeaderboardReportsRequest.to_json())

# convert the object into a dict
v1_cmp_leaderboard_reports_request_dict = v1_cmp_leaderboard_reports_request_instance.to_dict()
# create an instance of V1CmpLeaderboardReportsRequest from a dict
v1_cmp_leaderboard_reports_request_from_dict = V1CmpLeaderboardReportsRequest.from_dict(v1_cmp_leaderboard_reports_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



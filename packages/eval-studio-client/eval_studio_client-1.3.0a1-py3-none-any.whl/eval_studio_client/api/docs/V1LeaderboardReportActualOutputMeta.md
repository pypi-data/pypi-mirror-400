# V1LeaderboardReportActualOutputMeta

ActualOutputMeta represents the metadata about the actual output. Each instance can contain any combination of the fields below.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tokenization** | **str** | Optional. Actual output data tokenization like sentence_level_punkt. | [optional] 
**data** | [**List[V1LeaderboardReportActualOutputData]**](V1LeaderboardReportActualOutputData.md) | Optional. Actual output data - list of text fragments coupled with the metric values. | [optional] 
**agent_chat_activity_diagram** | [**V1AgentChatActivityDiagram**](V1AgentChatActivityDiagram.md) |  | [optional] 
**agent_chat_tools_bar_chart** | [**V1AgentChatToolsBarChart**](V1AgentChatToolsBarChart.md) |  | [optional] 
**agent_chat_scripts_bar_chart** | [**V1AgentChatScriptsBarChart**](V1AgentChatScriptsBarChart.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_leaderboard_report_actual_output_meta import V1LeaderboardReportActualOutputMeta

# TODO update the JSON string below
json = "{}"
# create an instance of V1LeaderboardReportActualOutputMeta from a JSON string
v1_leaderboard_report_actual_output_meta_instance = V1LeaderboardReportActualOutputMeta.from_json(json)
# print the JSON string representation of the object
print(V1LeaderboardReportActualOutputMeta.to_json())

# convert the object into a dict
v1_leaderboard_report_actual_output_meta_dict = v1_leaderboard_report_actual_output_meta_instance.to_dict()
# create an instance of V1LeaderboardReportActualOutputMeta from a dict
v1_leaderboard_report_actual_output_meta_from_dict = V1LeaderboardReportActualOutputMeta.from_dict(v1_leaderboard_report_actual_output_meta_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



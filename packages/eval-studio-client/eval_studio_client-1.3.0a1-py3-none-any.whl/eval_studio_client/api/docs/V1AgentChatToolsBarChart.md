# V1AgentChatToolsBarChart

AgentChatToolsBarChart represents the bar chart for agent chat tools usage.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tools** | [**Dict[str, V1AgentChatToolUsage]**](V1AgentChatToolUsage.md) | Output only. Map of tool name to tool usage statistics. | [optional] [readonly] 

## Example

```python
from eval_studio_client.api.models.v1_agent_chat_tools_bar_chart import V1AgentChatToolsBarChart

# TODO update the JSON string below
json = "{}"
# create an instance of V1AgentChatToolsBarChart from a JSON string
v1_agent_chat_tools_bar_chart_instance = V1AgentChatToolsBarChart.from_json(json)
# print the JSON string representation of the object
print(V1AgentChatToolsBarChart.to_json())

# convert the object into a dict
v1_agent_chat_tools_bar_chart_dict = v1_agent_chat_tools_bar_chart_instance.to_dict()
# create an instance of V1AgentChatToolsBarChart from a dict
v1_agent_chat_tools_bar_chart_from_dict = V1AgentChatToolsBarChart.from_dict(v1_agent_chat_tools_bar_chart_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



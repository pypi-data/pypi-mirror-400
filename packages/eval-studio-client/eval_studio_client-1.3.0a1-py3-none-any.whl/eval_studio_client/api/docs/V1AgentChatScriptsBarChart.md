# V1AgentChatScriptsBarChart

AgentChatScriptsBarChart represents the bar chart for agent chat scripts usage.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**scripts** | [**Dict[str, V1AgentChatScriptUsage]**](V1AgentChatScriptUsage.md) | Output only. Map of script name to script usage statistics. | [optional] [readonly] 

## Example

```python
from eval_studio_client.api.models.v1_agent_chat_scripts_bar_chart import V1AgentChatScriptsBarChart

# TODO update the JSON string below
json = "{}"
# create an instance of V1AgentChatScriptsBarChart from a JSON string
v1_agent_chat_scripts_bar_chart_instance = V1AgentChatScriptsBarChart.from_json(json)
# print the JSON string representation of the object
print(V1AgentChatScriptsBarChart.to_json())

# convert the object into a dict
v1_agent_chat_scripts_bar_chart_dict = v1_agent_chat_scripts_bar_chart_instance.to_dict()
# create an instance of V1AgentChatScriptsBarChart from a dict
v1_agent_chat_scripts_bar_chart_from_dict = V1AgentChatScriptsBarChart.from_dict(v1_agent_chat_scripts_bar_chart_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



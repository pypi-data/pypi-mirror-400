# V1AgentChatToolUsage

AgentChatToolUsage represents usage statistics for a single tool.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Output only. Name of the tool. | [optional] [readonly] 
**success_count** | **int** | Output only. Number of successful invocations. | [optional] [readonly] 
**failure_count** | **int** | Output only. Number of failed invocations. | [optional] [readonly] 
**total_count** | **int** | Output only. Total number of invocations. | [optional] [readonly] 

## Example

```python
from eval_studio_client.api.models.v1_agent_chat_tool_usage import V1AgentChatToolUsage

# TODO update the JSON string below
json = "{}"
# create an instance of V1AgentChatToolUsage from a JSON string
v1_agent_chat_tool_usage_instance = V1AgentChatToolUsage.from_json(json)
# print the JSON string representation of the object
print(V1AgentChatToolUsage.to_json())

# convert the object into a dict
v1_agent_chat_tool_usage_dict = v1_agent_chat_tool_usage_instance.to_dict()
# create an instance of V1AgentChatToolUsage from a dict
v1_agent_chat_tool_usage_from_dict = V1AgentChatToolUsage.from_dict(v1_agent_chat_tool_usage_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



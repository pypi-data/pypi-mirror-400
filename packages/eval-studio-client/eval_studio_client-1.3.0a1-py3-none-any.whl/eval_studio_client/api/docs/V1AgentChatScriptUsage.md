# V1AgentChatScriptUsage

AgentChatScriptUsage represents usage statistics for a single script.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Output only. Name of the script. | [optional] [readonly] 
**success_count** | **int** | Output only. Number of successful executions. | [optional] [readonly] 
**failure_count** | **int** | Output only. Number of failed executions. | [optional] [readonly] 
**total_count** | **int** | Output only. Total number of executions. | [optional] [readonly] 

## Example

```python
from eval_studio_client.api.models.v1_agent_chat_script_usage import V1AgentChatScriptUsage

# TODO update the JSON string below
json = "{}"
# create an instance of V1AgentChatScriptUsage from a JSON string
v1_agent_chat_script_usage_instance = V1AgentChatScriptUsage.from_json(json)
# print the JSON string representation of the object
print(V1AgentChatScriptUsage.to_json())

# convert the object into a dict
v1_agent_chat_script_usage_dict = v1_agent_chat_script_usage_instance.to_dict()
# create an instance of V1AgentChatScriptUsage from a dict
v1_agent_chat_script_usage_from_dict = V1AgentChatScriptUsage.from_dict(v1_agent_chat_script_usage_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



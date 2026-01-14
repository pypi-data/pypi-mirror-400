# V1AgentChatActivityDiagramNode

AgentChatActivityDiagramNode represents a node in the activity diagram.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Output only. Unique identifier for the node. | [optional] [readonly] 
**role** | **str** | Output only. Role of the node (runtime, user, agent, assistant, etc.). | [optional] [readonly] 
**label** | **str** | Output only. Label for the node. | [optional] [readonly] 

## Example

```python
from eval_studio_client.api.models.v1_agent_chat_activity_diagram_node import V1AgentChatActivityDiagramNode

# TODO update the JSON string below
json = "{}"
# create an instance of V1AgentChatActivityDiagramNode from a JSON string
v1_agent_chat_activity_diagram_node_instance = V1AgentChatActivityDiagramNode.from_json(json)
# print the JSON string representation of the object
print(V1AgentChatActivityDiagramNode.to_json())

# convert the object into a dict
v1_agent_chat_activity_diagram_node_dict = v1_agent_chat_activity_diagram_node_instance.to_dict()
# create an instance of V1AgentChatActivityDiagramNode from a dict
v1_agent_chat_activity_diagram_node_from_dict = V1AgentChatActivityDiagramNode.from_dict(v1_agent_chat_activity_diagram_node_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



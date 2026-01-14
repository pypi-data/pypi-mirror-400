# V1AgentChatActivityDiagram

AgentChatActivityDiagram represents the activity diagram for agent chat interactions.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rows** | [**List[V1AgentChatActivityDiagramRow]**](V1AgentChatActivityDiagramRow.md) | Output only. List of rows in the activity diagram. | [optional] [readonly] 
**edges** | [**List[V1AgentChatActivityDiagramEdge]**](V1AgentChatActivityDiagramEdge.md) | Output only. List of edges connecting nodes in the activity diagram. | [optional] [readonly] 

## Example

```python
from eval_studio_client.api.models.v1_agent_chat_activity_diagram import V1AgentChatActivityDiagram

# TODO update the JSON string below
json = "{}"
# create an instance of V1AgentChatActivityDiagram from a JSON string
v1_agent_chat_activity_diagram_instance = V1AgentChatActivityDiagram.from_json(json)
# print the JSON string representation of the object
print(V1AgentChatActivityDiagram.to_json())

# convert the object into a dict
v1_agent_chat_activity_diagram_dict = v1_agent_chat_activity_diagram_instance.to_dict()
# create an instance of V1AgentChatActivityDiagram from a dict
v1_agent_chat_activity_diagram_from_dict = V1AgentChatActivityDiagram.from_dict(v1_agent_chat_activity_diagram_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



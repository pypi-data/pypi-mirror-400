# V1AgentChatActivityDiagramEdge

AgentChatActivityDiagramEdge represents an edge connecting two nodes.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_from** | **str** | Output only. Source node ID. | [optional] [readonly] 
**to** | **str** | Output only. Target node ID. | [optional] [readonly] 
**label** | **str** | Output only. Label for the edge. | [optional] [readonly] 

## Example

```python
from eval_studio_client.api.models.v1_agent_chat_activity_diagram_edge import V1AgentChatActivityDiagramEdge

# TODO update the JSON string below
json = "{}"
# create an instance of V1AgentChatActivityDiagramEdge from a JSON string
v1_agent_chat_activity_diagram_edge_instance = V1AgentChatActivityDiagramEdge.from_json(json)
# print the JSON string representation of the object
print(V1AgentChatActivityDiagramEdge.to_json())

# convert the object into a dict
v1_agent_chat_activity_diagram_edge_dict = v1_agent_chat_activity_diagram_edge_instance.to_dict()
# create an instance of V1AgentChatActivityDiagramEdge from a dict
v1_agent_chat_activity_diagram_edge_from_dict = V1AgentChatActivityDiagramEdge.from_dict(v1_agent_chat_activity_diagram_edge_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



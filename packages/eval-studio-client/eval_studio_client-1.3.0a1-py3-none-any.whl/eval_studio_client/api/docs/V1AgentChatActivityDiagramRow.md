# V1AgentChatActivityDiagramRow

AgentChatActivityDiagramRow represents a row in the activity diagram.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**nodes** | [**List[V1AgentChatActivityDiagramNode]**](V1AgentChatActivityDiagramNode.md) | Output only. List of nodes in this row. | [optional] [readonly] 

## Example

```python
from eval_studio_client.api.models.v1_agent_chat_activity_diagram_row import V1AgentChatActivityDiagramRow

# TODO update the JSON string below
json = "{}"
# create an instance of V1AgentChatActivityDiagramRow from a JSON string
v1_agent_chat_activity_diagram_row_instance = V1AgentChatActivityDiagramRow.from_json(json)
# print the JSON string representation of the object
print(V1AgentChatActivityDiagramRow.to_json())

# convert the object into a dict
v1_agent_chat_activity_diagram_row_dict = v1_agent_chat_activity_diagram_row_instance.to_dict()
# create an instance of V1AgentChatActivityDiagramRow from a dict
v1_agent_chat_activity_diagram_row_from_dict = V1AgentChatActivityDiagramRow.from_dict(v1_agent_chat_activity_diagram_row_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



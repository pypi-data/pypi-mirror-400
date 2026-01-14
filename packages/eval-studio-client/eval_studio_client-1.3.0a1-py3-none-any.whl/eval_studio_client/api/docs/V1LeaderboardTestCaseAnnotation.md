# V1LeaderboardTestCaseAnnotation


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] [readonly] 
**create_time** | **datetime** | Output only. Timestamp when the LeaderboardTestCaseAnnotation was created. | [optional] [readonly] 
**creator** | **str** | Output only. Name of the user or service that requested creation of the LeaderboardTestCaseAnnotation. | [optional] [readonly] 
**update_time** | **datetime** | Output only. Optional. Timestamp when the LeaderboardTestCaseAnnotation was last updated. | [optional] [readonly] 
**updater** | **str** | Output only. Optional. Name of the user or service that requested update of the LeaderboardTestCaseAnnotation. | [optional] [readonly] 
**parent** | **str** | Parent Leaderboard Test Case resource name. e.g.: \&quot;leaderboards/&lt;UUID&gt;/testCases/&lt;UUID&gt;\&quot;. | [optional] 
**key** | **str** | Immutable. Annotation key. | [optional] 
**value** | **object** | Annotation value. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_leaderboard_test_case_annotation import V1LeaderboardTestCaseAnnotation

# TODO update the JSON string below
json = "{}"
# create an instance of V1LeaderboardTestCaseAnnotation from a JSON string
v1_leaderboard_test_case_annotation_instance = V1LeaderboardTestCaseAnnotation.from_json(json)
# print the JSON string representation of the object
print(V1LeaderboardTestCaseAnnotation.to_json())

# convert the object into a dict
v1_leaderboard_test_case_annotation_dict = v1_leaderboard_test_case_annotation_instance.to_dict()
# create an instance of V1LeaderboardTestCaseAnnotation from a dict
v1_leaderboard_test_case_annotation_from_dict = V1LeaderboardTestCaseAnnotation.from_dict(v1_leaderboard_test_case_annotation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



# V1UpdateLeaderboardTestCaseAnnotationResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**leaderboard_test_case_annotation** | [**V1LeaderboardTestCaseAnnotation**](V1LeaderboardTestCaseAnnotation.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_update_leaderboard_test_case_annotation_response import V1UpdateLeaderboardTestCaseAnnotationResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1UpdateLeaderboardTestCaseAnnotationResponse from a JSON string
v1_update_leaderboard_test_case_annotation_response_instance = V1UpdateLeaderboardTestCaseAnnotationResponse.from_json(json)
# print the JSON string representation of the object
print(V1UpdateLeaderboardTestCaseAnnotationResponse.to_json())

# convert the object into a dict
v1_update_leaderboard_test_case_annotation_response_dict = v1_update_leaderboard_test_case_annotation_response_instance.to_dict()
# create an instance of V1UpdateLeaderboardTestCaseAnnotationResponse from a dict
v1_update_leaderboard_test_case_annotation_response_from_dict = V1UpdateLeaderboardTestCaseAnnotationResponse.from_dict(v1_update_leaderboard_test_case_annotation_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



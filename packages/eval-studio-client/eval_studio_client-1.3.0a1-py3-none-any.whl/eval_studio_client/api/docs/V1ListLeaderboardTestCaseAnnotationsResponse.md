# V1ListLeaderboardTestCaseAnnotationsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**leaderboard_test_case_annotations** | [**List[V1LeaderboardTestCaseAnnotation]**](V1LeaderboardTestCaseAnnotation.md) | The list of LeaderboardTestCaseAnnotations. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_list_leaderboard_test_case_annotations_response import V1ListLeaderboardTestCaseAnnotationsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListLeaderboardTestCaseAnnotationsResponse from a JSON string
v1_list_leaderboard_test_case_annotations_response_instance = V1ListLeaderboardTestCaseAnnotationsResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListLeaderboardTestCaseAnnotationsResponse.to_json())

# convert the object into a dict
v1_list_leaderboard_test_case_annotations_response_dict = v1_list_leaderboard_test_case_annotations_response_instance.to_dict()
# create an instance of V1ListLeaderboardTestCaseAnnotationsResponse from a dict
v1_list_leaderboard_test_case_annotations_response_from_dict = V1ListLeaderboardTestCaseAnnotationsResponse.from_dict(v1_list_leaderboard_test_case_annotations_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



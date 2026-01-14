# eval_studio_client.api.LeaderboardTestCaseAnnotationServiceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**leaderboard_test_case_annotation_service_list_leaderboard_test_case_annotations**](LeaderboardTestCaseAnnotationServiceApi.md#leaderboard_test_case_annotation_service_list_leaderboard_test_case_annotations) | **GET** /v1/{parent_1}/annotations | 
[**leaderboard_test_case_annotation_service_update_leaderboard_test_case_annotation**](LeaderboardTestCaseAnnotationServiceApi.md#leaderboard_test_case_annotation_service_update_leaderboard_test_case_annotation) | **POST** /v1/{leaderboardTestCaseAnnotation.name} | 


# **leaderboard_test_case_annotation_service_list_leaderboard_test_case_annotations**
> V1ListLeaderboardTestCaseAnnotationsResponse leaderboard_test_case_annotation_service_list_leaderboard_test_case_annotations(parent_1)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_list_leaderboard_test_case_annotations_response import V1ListLeaderboardTestCaseAnnotationsResponse
from eval_studio_client.api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = eval_studio_client.api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with eval_studio_client.api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = eval_studio_client.api.LeaderboardTestCaseAnnotationServiceApi(api_client)
    parent_1 = 'parent_1_example' # str | Required. The parent resource name. Format: `leaderboards/{leaderboard}/testCases/{test_case}`. Use `leaderboards/{leaderboard}/testCases/-` to list across all test cases of a leaderboard. See https://google.aip.dev/159 for more details.

    try:
        api_response = api_instance.leaderboard_test_case_annotation_service_list_leaderboard_test_case_annotations(parent_1)
        print("The response of LeaderboardTestCaseAnnotationServiceApi->leaderboard_test_case_annotation_service_list_leaderboard_test_case_annotations:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LeaderboardTestCaseAnnotationServiceApi->leaderboard_test_case_annotation_service_list_leaderboard_test_case_annotations: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **parent_1** | **str**| Required. The parent resource name. Format: &#x60;leaderboards/{leaderboard}/testCases/{test_case}&#x60;. Use &#x60;leaderboards/{leaderboard}/testCases/-&#x60; to list across all test cases of a leaderboard. See https://google.aip.dev/159 for more details. | 

### Return type

[**V1ListLeaderboardTestCaseAnnotationsResponse**](V1ListLeaderboardTestCaseAnnotationsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**0** | An unexpected error response. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **leaderboard_test_case_annotation_service_update_leaderboard_test_case_annotation**
> V1UpdateLeaderboardTestCaseAnnotationResponse leaderboard_test_case_annotation_service_update_leaderboard_test_case_annotation(leaderboard_test_case_annotation_name, leaderboard_test_case_annotation, update_mask=update_mask, allow_missing=allow_missing)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.required_the_leaderboard_test_case_annotation_to_update import RequiredTheLeaderboardTestCaseAnnotationToUpdate
from eval_studio_client.api.models.v1_update_leaderboard_test_case_annotation_response import V1UpdateLeaderboardTestCaseAnnotationResponse
from eval_studio_client.api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = eval_studio_client.api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with eval_studio_client.api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = eval_studio_client.api.LeaderboardTestCaseAnnotationServiceApi(api_client)
    leaderboard_test_case_annotation_name = 'leaderboard_test_case_annotation_name_example' # str | Output only. Name of the LeaderboardTestCaseAnnotation resource. e.g.: \"leaderboards/<UUID>/testCases/<UUID>/annotations/<UUID>\"
    leaderboard_test_case_annotation = eval_studio_client.api.RequiredTheLeaderboardTestCaseAnnotationToUpdate() # RequiredTheLeaderboardTestCaseAnnotationToUpdate | Required. The LeaderboardTestCaseAnnotation to update.
    update_mask = 'update_mask_example' # str | Optional. The list of fields to update. If empty, all modifiable fields will be updated. The following fields can be updated:  - value (optional)
    allow_missing = True # bool | Optional. If true, the request is allowed to create a new LeaderboardTestCaseAnnotation if it is not found. (optional)

    try:
        api_response = api_instance.leaderboard_test_case_annotation_service_update_leaderboard_test_case_annotation(leaderboard_test_case_annotation_name, leaderboard_test_case_annotation, update_mask=update_mask, allow_missing=allow_missing)
        print("The response of LeaderboardTestCaseAnnotationServiceApi->leaderboard_test_case_annotation_service_update_leaderboard_test_case_annotation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LeaderboardTestCaseAnnotationServiceApi->leaderboard_test_case_annotation_service_update_leaderboard_test_case_annotation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **leaderboard_test_case_annotation_name** | **str**| Output only. Name of the LeaderboardTestCaseAnnotation resource. e.g.: \&quot;leaderboards/&lt;UUID&gt;/testCases/&lt;UUID&gt;/annotations/&lt;UUID&gt;\&quot; | 
 **leaderboard_test_case_annotation** | [**RequiredTheLeaderboardTestCaseAnnotationToUpdate**](RequiredTheLeaderboardTestCaseAnnotationToUpdate.md)| Required. The LeaderboardTestCaseAnnotation to update. | 
 **update_mask** | **str**| Optional. The list of fields to update. If empty, all modifiable fields will be updated. The following fields can be updated:  - value | [optional] 
 **allow_missing** | **bool**| Optional. If true, the request is allowed to create a new LeaderboardTestCaseAnnotation if it is not found. | [optional] 

### Return type

[**V1UpdateLeaderboardTestCaseAnnotationResponse**](V1UpdateLeaderboardTestCaseAnnotationResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**0** | An unexpected error response. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


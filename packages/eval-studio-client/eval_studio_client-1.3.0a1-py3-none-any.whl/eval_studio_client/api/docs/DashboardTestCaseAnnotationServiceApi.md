# eval_studio_client.api.DashboardTestCaseAnnotationServiceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**dashboard_test_case_annotation_service_list_dashboard_test_case_annotations**](DashboardTestCaseAnnotationServiceApi.md#dashboard_test_case_annotation_service_list_dashboard_test_case_annotations) | **GET** /v1/{parent}/annotations | 
[**dashboard_test_case_annotation_service_update_dashboard_test_case_annotation**](DashboardTestCaseAnnotationServiceApi.md#dashboard_test_case_annotation_service_update_dashboard_test_case_annotation) | **POST** /v1/{dashboardTestCaseAnnotation.name} | 


# **dashboard_test_case_annotation_service_list_dashboard_test_case_annotations**
> V1ListDashboardTestCaseAnnotationsResponse dashboard_test_case_annotation_service_list_dashboard_test_case_annotations(parent)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_list_dashboard_test_case_annotations_response import V1ListDashboardTestCaseAnnotationsResponse
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
    api_instance = eval_studio_client.api.DashboardTestCaseAnnotationServiceApi(api_client)
    parent = 'parent_example' # str | Required. The parent resource name. Format: `dashboards/{dashboard}/testCases/{test_case}`.  Wildcard support: Use the special value `-` for test_case to list annotations across all test cases within the specified dashboard: `dashboards/{dashboard}/testCases/-`  See https://google.aip.dev/159 for more details on collection identifiers.

    try:
        api_response = api_instance.dashboard_test_case_annotation_service_list_dashboard_test_case_annotations(parent)
        print("The response of DashboardTestCaseAnnotationServiceApi->dashboard_test_case_annotation_service_list_dashboard_test_case_annotations:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardTestCaseAnnotationServiceApi->dashboard_test_case_annotation_service_list_dashboard_test_case_annotations: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **parent** | **str**| Required. The parent resource name. Format: &#x60;dashboards/{dashboard}/testCases/{test_case}&#x60;.  Wildcard support: Use the special value &#x60;-&#x60; for test_case to list annotations across all test cases within the specified dashboard: &#x60;dashboards/{dashboard}/testCases/-&#x60;  See https://google.aip.dev/159 for more details on collection identifiers. | 

### Return type

[**V1ListDashboardTestCaseAnnotationsResponse**](V1ListDashboardTestCaseAnnotationsResponse.md)

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

# **dashboard_test_case_annotation_service_update_dashboard_test_case_annotation**
> V1UpdateDashboardTestCaseAnnotationResponse dashboard_test_case_annotation_service_update_dashboard_test_case_annotation(dashboard_test_case_annotation_name, dashboard_test_case_annotation, update_mask=update_mask, allow_missing=allow_missing)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.required_the_dashboard_test_case_annotation_to_update import RequiredTheDashboardTestCaseAnnotationToUpdate
from eval_studio_client.api.models.v1_update_dashboard_test_case_annotation_response import V1UpdateDashboardTestCaseAnnotationResponse
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
    api_instance = eval_studio_client.api.DashboardTestCaseAnnotationServiceApi(api_client)
    dashboard_test_case_annotation_name = 'dashboard_test_case_annotation_name_example' # str | Output only. Name of the DashboardTestCaseAnnotation resource. e.g.: \"dashboards/<UUID>/testCases/<UUID>/annotations/<UUID>\"
    dashboard_test_case_annotation = eval_studio_client.api.RequiredTheDashboardTestCaseAnnotationToUpdate() # RequiredTheDashboardTestCaseAnnotationToUpdate | Required. The DashboardTestCaseAnnotation to update.
    update_mask = 'update_mask_example' # str | Optional. The list of fields to update. If empty, all modifiable fields will be updated. The following fields can be updated:  - value (optional)
    allow_missing = True # bool | Optional. If true, the request is allowed to create a new DashboardTestCaseAnnotation if it is not found. (optional)

    try:
        api_response = api_instance.dashboard_test_case_annotation_service_update_dashboard_test_case_annotation(dashboard_test_case_annotation_name, dashboard_test_case_annotation, update_mask=update_mask, allow_missing=allow_missing)
        print("The response of DashboardTestCaseAnnotationServiceApi->dashboard_test_case_annotation_service_update_dashboard_test_case_annotation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardTestCaseAnnotationServiceApi->dashboard_test_case_annotation_service_update_dashboard_test_case_annotation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dashboard_test_case_annotation_name** | **str**| Output only. Name of the DashboardTestCaseAnnotation resource. e.g.: \&quot;dashboards/&lt;UUID&gt;/testCases/&lt;UUID&gt;/annotations/&lt;UUID&gt;\&quot; | 
 **dashboard_test_case_annotation** | [**RequiredTheDashboardTestCaseAnnotationToUpdate**](RequiredTheDashboardTestCaseAnnotationToUpdate.md)| Required. The DashboardTestCaseAnnotation to update. | 
 **update_mask** | **str**| Optional. The list of fields to update. If empty, all modifiable fields will be updated. The following fields can be updated:  - value | [optional] 
 **allow_missing** | **bool**| Optional. If true, the request is allowed to create a new DashboardTestCaseAnnotation if it is not found. | [optional] 

### Return type

[**V1UpdateDashboardTestCaseAnnotationResponse**](V1UpdateDashboardTestCaseAnnotationResponse.md)

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


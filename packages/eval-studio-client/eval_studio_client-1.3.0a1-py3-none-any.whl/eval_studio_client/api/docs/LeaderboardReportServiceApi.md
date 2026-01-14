# eval_studio_client.api.LeaderboardReportServiceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**leaderboard_report_service_cmp_leaderboard_reports**](LeaderboardReportServiceApi.md#leaderboard_report_service_cmp_leaderboard_reports) | **POST** /v1/leaderboardReports:compare | 
[**leaderboard_report_service_get_leaderboard_report**](LeaderboardReportServiceApi.md#leaderboard_report_service_get_leaderboard_report) | **GET** /v1/{name_4} | 


# **leaderboard_report_service_cmp_leaderboard_reports**
> V1CmpLeaderboardReportsResponse leaderboard_report_service_cmp_leaderboard_reports(body)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_cmp_leaderboard_reports_request import V1CmpLeaderboardReportsRequest
from eval_studio_client.api.models.v1_cmp_leaderboard_reports_response import V1CmpLeaderboardReportsResponse
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
    api_instance = eval_studio_client.api.LeaderboardReportServiceApi(api_client)
    body = eval_studio_client.api.V1CmpLeaderboardReportsRequest() # V1CmpLeaderboardReportsRequest | 

    try:
        api_response = api_instance.leaderboard_report_service_cmp_leaderboard_reports(body)
        print("The response of LeaderboardReportServiceApi->leaderboard_report_service_cmp_leaderboard_reports:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LeaderboardReportServiceApi->leaderboard_report_service_cmp_leaderboard_reports: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**V1CmpLeaderboardReportsRequest**](V1CmpLeaderboardReportsRequest.md)|  | 

### Return type

[**V1CmpLeaderboardReportsResponse**](V1CmpLeaderboardReportsResponse.md)

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

# **leaderboard_report_service_get_leaderboard_report**
> V1GetLeaderboardReportResponse leaderboard_report_service_get_leaderboard_report(name_4, view=view)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_get_leaderboard_report_response import V1GetLeaderboardReportResponse
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
    api_instance = eval_studio_client.api.LeaderboardReportServiceApi(api_client)
    name_4 = 'name_4_example' # str | Required. The name of the Leaderboard to retrieve.
    view = 'LEADERBOARD_REPORT_RESULT_VIEW_UNSPECIFIED' # str | Optional. The view of the leaderboard report results to return. Defaults to LEADERBOARD_REPORT_RESULT_VIEW_FULL.   - LEADERBOARD_REPORT_RESULT_VIEW_UNSPECIFIED: Default value. The basic view with essential fields.  - LEADERBOARD_REPORT_RESULT_VIEW_FULL: Full view with all fields populated.  - LEADERBOARD_REPORT_RESULT_VIEW_SUMMARY: Summary view with only key fields. (optional) (default to 'LEADERBOARD_REPORT_RESULT_VIEW_UNSPECIFIED')

    try:
        api_response = api_instance.leaderboard_report_service_get_leaderboard_report(name_4, view=view)
        print("The response of LeaderboardReportServiceApi->leaderboard_report_service_get_leaderboard_report:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LeaderboardReportServiceApi->leaderboard_report_service_get_leaderboard_report: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name_4** | **str**| Required. The name of the Leaderboard to retrieve. | 
 **view** | **str**| Optional. The view of the leaderboard report results to return. Defaults to LEADERBOARD_REPORT_RESULT_VIEW_FULL.   - LEADERBOARD_REPORT_RESULT_VIEW_UNSPECIFIED: Default value. The basic view with essential fields.  - LEADERBOARD_REPORT_RESULT_VIEW_FULL: Full view with all fields populated.  - LEADERBOARD_REPORT_RESULT_VIEW_SUMMARY: Summary view with only key fields. | [optional] [default to &#39;LEADERBOARD_REPORT_RESULT_VIEW_UNSPECIFIED&#39;]

### Return type

[**V1GetLeaderboardReportResponse**](V1GetLeaderboardReportResponse.md)

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


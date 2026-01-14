# eval_studio_client.api.DashboardReportServiceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**dashboard_report_service_get_dashboard_report**](DashboardReportServiceApi.md#dashboard_report_service_get_dashboard_report) | **GET** /v1/{name} | 


# **dashboard_report_service_get_dashboard_report**
> V1GetDashboardReportResponse dashboard_report_service_get_dashboard_report(name)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_get_dashboard_report_response import V1GetDashboardReportResponse
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
    api_instance = eval_studio_client.api.DashboardReportServiceApi(api_client)
    name = 'name_example' # str | Required. The name of the Dashboard to retrieve.

    try:
        api_response = api_instance.dashboard_report_service_get_dashboard_report(name)
        print("The response of DashboardReportServiceApi->dashboard_report_service_get_dashboard_report:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardReportServiceApi->dashboard_report_service_get_dashboard_report: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Required. The name of the Dashboard to retrieve. | 

### Return type

[**V1GetDashboardReportResponse**](V1GetDashboardReportResponse.md)

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


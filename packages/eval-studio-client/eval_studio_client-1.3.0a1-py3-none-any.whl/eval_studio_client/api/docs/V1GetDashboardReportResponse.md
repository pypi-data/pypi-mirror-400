# V1GetDashboardReportResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dashboard_report** | [**V1DashboardReport**](V1DashboardReport.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_get_dashboard_report_response import V1GetDashboardReportResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1GetDashboardReportResponse from a JSON string
v1_get_dashboard_report_response_instance = V1GetDashboardReportResponse.from_json(json)
# print the JSON string representation of the object
print(V1GetDashboardReportResponse.to_json())

# convert the object into a dict
v1_get_dashboard_report_response_dict = v1_get_dashboard_report_response_instance.to_dict()
# create an instance of V1GetDashboardReportResponse from a dict
v1_get_dashboard_report_response_from_dict = V1GetDashboardReportResponse.from_dict(v1_get_dashboard_report_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



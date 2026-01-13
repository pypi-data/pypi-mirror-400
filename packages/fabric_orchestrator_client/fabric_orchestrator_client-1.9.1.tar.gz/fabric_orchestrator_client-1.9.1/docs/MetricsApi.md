# swagger_client.MetricsApi

All URIs are relative to *http://127.0.0.1:8700/*

Method | HTTP request | Description
------------- | ------------- | -------------
[**metrics_overview_get**](MetricsApi.md#metrics_overview_get) | **GET** /metrics/overview | Control Framework metrics overview

# **metrics_overview_get**
> Metrics metrics_overview_get(excluded_projects=excluded_projects)

Control Framework metrics overview

Control Framework metrics overview

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MetricsApi()
excluded_projects = ['excluded_projects_example'] # list[str] | List of projects to exclude from the metrics overview (optional)

try:
    # Control Framework metrics overview
    api_response = api_instance.metrics_overview_get(excluded_projects=excluded_projects)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MetricsApi->metrics_overview_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **excluded_projects** | [**list[str]**](str.md)| List of projects to exclude from the metrics overview | [optional] 

### Return type

[**Metrics**](Metrics.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


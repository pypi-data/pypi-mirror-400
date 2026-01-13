# SliversApi

All URIs are relative to *http://127.0.0.1:8700/*

Method | HTTP request | Description
------------- | ------------- | -------------
[**slivers_get**](SliversApi.md#slivers_get) | **GET** /slivers | Retrieve a listing of user slivers
[**slivers_sliver_id_get**](SliversApi.md#slivers_sliver_id_get) | **GET** /slivers/{sliver_id} | slivers properties

# **slivers_get**
> Slivers slivers_get(slice_id, as_self=as_self)

Retrieve a listing of user slivers

Retrieve a listing of user slivers

### Example
```python
from __future__ import print_function
import time
from fabric_cf.orchestrator.swagger_client import SliversApi, Configuration, ApiClient
from fabric_cf.orchestrator.swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: bearerAuth
configuration = Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = SliversApi(ApiClient(configuration))
slice_id = 'slice_id_example' # str | Slice identifier as UUID
as_self = True # bool | GET object as Self (optional) (default to true)

try:
    # Retrieve a listing of user slivers
    api_response = api_instance.slivers_get(slice_id, as_self=as_self)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SliversApi->slivers_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **slice_id** | **str**| Slice identifier as UUID | 
 **as_self** | **bool**| GET object as Self | [optional] [default to true]

### Return type

[**Slivers**](Slivers.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **slivers_sliver_id_get**
> Slivers slivers_sliver_id_get(slice_id, sliver_id, as_self=as_self)

slivers properties

Retrieve Sliver properties

### Example
```python
from __future__ import print_function
import time
from fabric_cf.orchestrator.swagger_client import SliversApi, Configuration, ApiClient
from fabric_cf.orchestrator.swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: bearerAuth
configuration = Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = SliversApi(ApiClient(configuration))

slice_id = 'slice_id_example' # str | Slice identified by universally unique identifier
sliver_id = 'sliver_id_example' # str | Sliver identified by universally unique identifier
as_self = True # bool | GET object as Self (optional) (default to true)

try:
    # slivers properties
    api_response = api_instance.slivers_sliver_id_get(slice_id, sliver_id, as_self=as_self)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SliversApi->slivers_sliver_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **slice_id** | **str**| Slice identified by universally unique identifier | 
 **sliver_id** | **str**| Sliver identified by universally unique identifier | 
 **as_self** | **bool**| GET object as Self | [optional] [default to true]

### Return type

[**Slivers**](Slivers.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


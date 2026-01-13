# swagger_client.PoasApi

All URIs are relative to *http://127.0.0.1:8700/*

Method | HTTP request | Description
------------- | ------------- | -------------
[**poas_create_sliver_id_post**](PoasApi.md#poas_create_sliver_id_post) | **POST** /poas/create/{sliver_id} | Perform an operational action on a sliver.
[**poas_get**](PoasApi.md#poas_get) | **GET** /poas/ | Request get the status of the POAs.
[**poas_poa_id_get**](PoasApi.md#poas_poa_id_get) | **GET** /poas/{poa_id} | Perform an operational action on a sliver.

# **poas_create_sliver_id_post**
> Poa poas_create_sliver_id_post(body, sliver_id)

Perform an operational action on a sliver.

Request to perform an operation action on a sliver. Supported actions include - reboot a VM sliver, get cpu info, get numa info, pin vCPUs, pin memory to a numa node etc.   

### Example
```python
from __future__ import print_function
import time
from fabric_cf.orchestrator.swagger_client import PoasApi, PoaPost, Configuration, ApiClient
from fabric_cf.orchestrator.swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: bearerAuth
configuration = Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = PoasApi(ApiClient(configuration))
body = PoaPost() # PoaPost | Perform Operation Action
sliver_id = 'sliver_id_example' # str | Sliver identified by universally unique identifier

try:
    # Perform an operational action on a sliver.
    api_response = api_instance.poas_create_sliver_id_post(body, sliver_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PoasApi->poas_create_sliver_id_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**PoaPost**](PoaPost.md)| Perform Operation Action | 
 **sliver_id** | **str**| Sliver identified by universally unique identifier | 

### Return type

[**Poa**](Poa.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **poas_get**
> Poa poas_get(sliver_id=sliver_id, states=states, limit=limit, offset=offset)

Request get the status of the POAs.

Request get the status of the POAs   

### Example
```python
from __future__ import print_function
import time
from fabric_cf.orchestrator.swagger_client import PoasApi, PoaPost, Configuration, ApiClient
from fabric_cf.orchestrator.swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: bearerAuth
configuration = Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'


# create an instance of the API class
api_instance = PoasApi(ApiClient(configuration))
sliver_id = 'sliver_id_example' # str | Search for POAs for a sliver (optional)
states = ['states_example'] # list[str] | Search for POAs in the specified states (optional)
limit = 5 # int | maximum number of results to return per page (1 or more) (optional) (default to 5)
offset = 0 # int | number of items to skip before starting to collect the result set (optional) (default to 0)

try:
    # Request get the status of the POAs.
    api_response = api_instance.poas_get(sliver_id=sliver_id, states=states, limit=limit, offset=offset)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PoasApi->poas_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sliver_id** | **str**| Search for POAs for a sliver | [optional] 
 **states** | [**list[str]**](str.md)| Search for POAs in the specified states | [optional] 
 **limit** | **int**| maximum number of results to return per page (1 or more) | [optional] [default to 5]
 **offset** | **int**| number of items to skip before starting to collect the result set | [optional] [default to 0]

### Return type

[**Poa**](Poa.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **poas_poa_id_get**
> Poa poas_poa_id_get(poa_id)

Perform an operational action on a sliver.

Request get the status of the POA identified by poa_id.   

### Example
```python
from __future__ import print_function
import time
from fabric_cf.orchestrator.swagger_client import PoasApi, PoaPost, Configuration, ApiClient
from fabric_cf.orchestrator.swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: bearerAuth
configuration = Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = PoasApi(ApiClient(configuration))
poa_id = 'poa_id_example' # str | Poa Id for the POA triggered

try:
    # Perform an operational action on a sliver.
    api_response = api_instance.poas_poa_id_get(poa_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PoasApi->poas_poa_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **poa_id** | **str**| Poa Id for the POA triggered | 

### Return type

[**Poa**](Poa.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


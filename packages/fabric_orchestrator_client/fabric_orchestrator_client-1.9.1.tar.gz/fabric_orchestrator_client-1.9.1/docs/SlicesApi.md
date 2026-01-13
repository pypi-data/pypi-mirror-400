# SlicesApi

All URIs are relative to *http://127.0.0.1:8700/*

Method | HTTP request | Description
------------- | ------------- | -------------
[**slices_create_post**](SlicesApi.md#slices_create_post) | **POST** /slices/create | Create slice
[**slices_creates_post**](SlicesApi.md#slices_creates_post) | **POST** /slices/creates | Create slice
[**slices_delete_delete**](SlicesApi.md#slices_delete_delete) | **DELETE** /slices/delete | Delete all slices for a User within a project.
[**slices_delete_slice_id_delete**](SlicesApi.md#slices_delete_slice_id_delete) | **DELETE** /slices/delete/{slice_id} | Delete slice.
[**slices_get**](SlicesApi.md#slices_get) | **GET** /slices | Retrieve a listing of user slices
[**slices_modify_slice_id_accept_post**](SlicesApi.md#slices_modify_slice_id_accept_post) | **POST** /slices/modify/{slice_id}/accept | Accept the last modify an existing slice
[**slices_modify_slice_id_put**](SlicesApi.md#slices_modify_slice_id_put) | **PUT** /slices/modify/{slice_id} | Modify an existing slice
[**slices_renew_slice_id_post**](SlicesApi.md#slices_renew_slice_id_post) | **POST** /slices/renew/{slice_id} | Renew slice
[**slices_slice_id_get**](SlicesApi.md#slices_slice_id_get) | **GET** /slices/{slice_id} | slice properties

# **slices_create_post**
> Slivers slices_create_post(body, name, ssh_key, lease_end_time=lease_end_time)

Create slice

Request to create slice as described in the request. Request would be a graph ML describing the requested resources. Resources may be requested to be created now or in future. On success, one or more slivers are allocated, containing resources satisfying the request, and assigned to the given slice. This API returns list and description of the resources reserved for the slice in the form of Graph ML. Orchestrator would also trigger provisioning of these resources asynchronously on the appropriate sites either now or in the future as requested. Experimenter can invoke get slice API to get the latest state of the requested resources.  

### Example
```python
from __future__ import print_function
import time
from fabric_cf.orchestrator.swagger_client import SlicesApi, Configuration, ApiClient
from fabric_cf.orchestrator.swagger_client.rest import ApiException
from fabric_cf.orchestrator.swagger_client.models import SlicesPost
from pprint import pprint

# Configure API key authorization: bearerAuth
configuration = Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = SlicesApi(ApiClient(configuration))
body = 'body_example' # str | 
name = 'name_example' # str | Slice Name
ssh_key = 'ssh_key_example' # str | User SSH Key
lease_end_time = 'lease_end_time_example' # str | Lease End Time for the Slice (optional)

try:
    # Create slice
    api_response = api_instance.slices_create_post(body, name, ssh_key, lease_end_time=lease_end_time)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlicesApi->slices_create_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**str**](str.md)|  | 
 **name** | **str**| Slice Name | 
 **ssh_key** | **str**| User SSH Key | 
 **lease_end_time** | **str**| Lease End Time for the Slice | [optional] 

### Return type

[**Slivers**](Slivers.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **slices_creates_post**
> Slivers slices_creates_post(body, name, lifetime=lifetime, lease_start_time=lease_start_time, lease_end_time=lease_end_time)

Create slice

Request to create slice as described in the request. Request would be a graph ML describing the requested resources. Resources may be requested to be created now or in future. On success, one or more slivers are allocated, containing resources satisfying the request, and assigned to the given slice. This API returns list and description of the resources reserved for the slice in the form of Graph ML. Orchestrator would also trigger provisioning of these resources asynchronously on the appropriate sites either now or in the future as requested. Experimenter can invoke get slice API to get the latest state of the requested resources.  

### Example
```python
from __future__ import print_function
from fabric_cf.orchestrator.swagger_client import SlicesApi, Configuration, ApiClient
from fabric_cf.orchestrator.swagger_client.rest import ApiException
from fabric_cf.orchestrator.swagger_client.models import SlicesPost
from pprint import pprint

# Configure API key authorization: bearerAuth
configuration = Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'


# create an instance of the API class
api_instance = SlicesApi(ApiClient(configuration))
body = SlicesPost() # SlicesPost | Create new Slice
name = 'name_example' # str | Slice Name
lifetime = 24 # int | Lifetime of the slice requested in hours. (optional) (default to 24)
lease_start_time = 'lease_start_time_example' # str | Lease End Time for the Slice (optional)
lease_end_time = 'lease_end_time_example' # str | Lease End Time for the Slice (optional)

try:
    # Create slice
    api_response = api_instance.slices_creates_post(body, name, lifetime=lifetime, lease_start_time=lease_start_time, lease_end_time=lease_end_time)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlicesApi->slices_creates_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**SlicesPost**](SlicesPost.md)| Create new Slice | 
 **name** | **str**| Slice Name | 
 **lifetime** | **int**| Lifetime of the slice requested in hours. | [optional] [default to 24]
 **lease_start_time** | **str**| Lease End Time for the Slice | [optional] 
 **lease_end_time** | **str**| Lease End Time for the Slice | [optional] 

### Return type

[**Slivers**](Slivers.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **slices_delete_delete**
> Status200OkNoContent slices_delete_delete()

Delete all slices for a User within a project.

Delete all slices for a User within a project. User identity email and project id is available in the bearer token. 

### Example
```python
from __future__ import print_function
import time
from fabric_cf.orchestrator.swagger_client import SlicesApi, Configuration, ApiClient
from fabric_cf.orchestrator.swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: bearerAuth
configuration = Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = SlicesApi(ApiClient(configuration))
email = 'email_example' # str | User's email address

try:
    # Delete all slices for a User within a project.
    api_response = api_instance.slices_delete_delete()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlicesApi->slices_delete_delete: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**Status200OkNoContent**](Status200OkNoContent.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **slices_delete_slice_id_delete**
> Status200OkNoContent slices_delete_slice_id_delete(slice_id)

Delete slice.

Request to delete slice. On success, resources associated with slice or sliver are stopped if necessary, de-provisioned and un-allocated at the respective sites. 

### Example
```python
from __future__ import print_function
import time
from fabric_cf.orchestrator.swagger_client import SlicesApi, Configuration, ApiClient
from fabric_cf.orchestrator.swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: bearerAuth
configuration = Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = SlicesApi(ApiClient(configuration))
slice_id = 'slice_id_example' # str | Slice identified by universally unique identifier

try:
    # Delete slice.
    api_response = api_instance.slices_delete_slice_id_delete(slice_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlicesApi->slices_delete_slice_id_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **slice_id** | **str**| Slice identified by universally unique identifier | 

### Return type

[**Status200OkNoContent**](Status200OkNoContent.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **slices_get**
> Slices slices_get(name=name, search=search, exact_match=exact_match, as_self=as_self, states=states, limit=limit, offset=offset)

Retrieve a listing of user slices

Retrieve a listing of user slices. It returns list of all slices belonging to all members in a project when 'as_self' is False otherwise returns only the all user's slices in a project.

### Example
```python
from __future__ import print_function
import time
from fabric_cf.orchestrator.swagger_client import SlicesApi, Configuration, ApiClient
from fabric_cf.orchestrator.swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: bearerAuth
configuration = Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = SlicesApi(ApiClient(configuration))
name = 'name_example' # str | Search for Slices with the name (optional)
search = 'search_example' # str | search term applied (optional)
exact_match = false # bool | Exact Match for Search term (optional) (default to false)
as_self = true # bool | GET object as Self (optional) (default to true)
states = ['states_example'] # list[str] | Search for Slices in the specified states (optional)
limit = 5 # int | maximum number of results to return per page (1 or more) (optional) (default to 5)
offset = 0 # int | number of items to skip before starting to collect the result set (optional) (default to 0)

try:
    # Retrieve a listing of user slices
    api_response = api_instance.slices_get(name=name, search=search, exact_match=exact_match, as_self=as_self, states=states, limit=limit, offset=offset)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlicesApi->slices_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Search for Slices with the name | [optional] 
 **search** | **str**| search term applied | [optional] 
 **exact_match** | **bool**| Exact Match for Search term | [optional] [default to false]
 **as_self** | **bool**| GET object as Self | [optional] [default to true]
 **states** | [**list[str]**](str.md)| Search for Slices in the specified states | [optional] 
 **limit** | **int**| maximum number of results to return per page (1 or more) | [optional] [default to 5]
 **offset** | **int**| number of items to skip before starting to collect the result set | [optional] [default to 0]

### Return type

[**Slices**](Slices.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **slices_modify_slice_id_accept_post**
> SliceDetails slices_modify_slice_id_accept_post(slice_id)

Accept the last modify an existing slice

Accept the last modify and prune any failed resources from the Slice. Also return the accepted slice model back to the user.  

### Example
```python
from __future__ import print_function
import time
from fabric_cf.orchestrator.swagger_client import SlicesApi, Configuration, ApiClient
from fabric_cf.orchestrator.swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: bearerAuth
configuration = Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'


# create an instance of the API class
api_instance = SlicesApi(ApiClient(configuration))
slice_id = 'slice_id_example' # str | Slice identified by universally unique identifier

try:
    # Accept the last modify an existing slice
    api_response = api_instance.slices_modify_slice_id_accept_post(slice_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlicesApi->slices_modify_slice_id_accept_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **slice_id** | **str**| Slice identified by universally unique identifier | 

### Return type

[**SliceDetails**](SliceDetails.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **slices_modify_slice_id_put**
> Slivers slices_modify_slice_id_put(body, slice_id)

Modify an existing slice

Request to modify an existing slice as described in the request. Request would be a graph ML describing the experiment topolgy expected after a modify. The supported modify actions include adding or removing nodes, components, network services or interfaces of the slice. On success, one or more slivers are allocated, containing resources satisfying the request, and assigned to the given slice. This API returns list and description of the resources reserved for the slice in the form of Graph ML. Orchestrator would also trigger provisioning of these resources asynchronously on the appropriate sites either now or in the future as requested. Experimenter can invoke get slice API to get the latest state of the requested resources.  

### Example
```python
from __future__ import print_function
import time
from fabric_cf.orchestrator.swagger_client import SlicesApi, Configuration, ApiClient
from fabric_cf.orchestrator.swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: bearerAuth
configuration = Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = SlicesApi(ApiClient(configuration))
body = 'body_example' # str | Modify a Slice
slice_id = 'slice_id_example' # str | Slice identified by universally unique identifier

try:
    # Modify an existing slice
    api_response = api_instance.slices_modify_slice_id_put(body, slice_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlicesApi->slices_modify_slice_id_put: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**str**](str.md)| Modify a Slice | 
 **slice_id** | **str**| Slice identified by universally unique identifier | 

### Return type

[**Slivers**](Slivers.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: text/plain
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **slices_renew_slice_id_post**
> Status200OkNoContent slices_renew_slice_id_post(slice_id, lease_end_time)

Renew slice

Request to extend slice be renewed with their expiration extended. If possible, the orchestrator should extend the slivers to the requested expiration time, or to a sooner time if policy limits apply. 

### Example
```python
from __future__ import print_function
import time
from fabric_cf.orchestrator.swagger_client import SlicesApi, Configuration, ApiClient
from fabric_cf.orchestrator.swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: bearerAuth
configuration = Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = SlicesApi(ApiClient(configuration))
slice_id = 'slice_id_example' # str | Slice identified by universally unique identifier
lease_end_time = 'lease_end_time_example' # str | New Lease End Time for the Slice

try:
    # Renew slice
    api_response = api_instance.slices_renew_slice_id_post(slice_id, lease_end_time)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlicesApi->slices_renew_slice_id_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **slice_id** | **str**| Slice identified by universally unique identifier | 
 **lease_end_time** | **str**| New Lease End Time for the Slice | 

### Return type

[**Status200OkNoContent**](Status200OkNoContent.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **slices_slice_id_get**
> SliceDetails slices_slice_id_get(slice_id, graph_format, as_self=as_self)

slice properties

Retrieve Slice properties

### Example
```python
from __future__ import print_function
import time
from fabric_cf.orchestrator.swagger_client import SlicesApi, Configuration, ApiClient
from fabric_cf.orchestrator.swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: bearerAuth
configuration = Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = SlicesApi(ApiClient(configuration))
slice_id = 'slice_id_example' # str | Slice identified by universally unique identifier
graph_format = 'GRAPHML' # str | graph format (default to GRAPHML)
as_self = true # bool | GET object as Self (optional) (default to true)

try:
    # slice properties
    api_response = api_instance.slices_slice_id_get(slice_id, graph_format, as_self=as_self)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlicesApi->slices_slice_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **slice_id** | **str**| Slice identified by universally unique identifier | 
 **graph_format** | **str**| graph format | [default to GRAPHML]
 **as_self** | **bool**| GET object as Self | [optional] [default to true]

### Return type

[**SliceDetails**](SliceDetails.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


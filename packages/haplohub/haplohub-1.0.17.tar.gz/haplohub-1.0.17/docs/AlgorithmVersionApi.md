# haplohub.AlgorithmVersionApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_algorithm_version**](AlgorithmVersionApi.md#get_algorithm_version) | **GET** /api/v1/algorithm-version/{algorithm_version_id}/ | Get algorithm version
[**list_algorithm_versions**](AlgorithmVersionApi.md#list_algorithm_versions) | **GET** /api/v1/algorithm-version/ | List algorithm versions


# **get_algorithm_version**
> ResultResponseAlgorithmVersionSchema get_algorithm_version(algorithm_version_id)

Get algorithm version

Retrieve an algorithm version definition by its identifier.

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.result_response_algorithm_version_schema import ResultResponseAlgorithmVersionSchema
from haplohub.rest import ApiException
from pprint import pprint

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: 
configuration = haplohub.Configuration(
    access_token=os.environ["API_KEY"]
)
# Enter a context with an instance of the API client
with haplohub.ApiClient(configuration) as api_client:
    algorithm_version_id = 'algorithm_version_id_example' # str | 

    try:
        # Get algorithm version
        api_response = api_client.algorithm_version_api.get_algorithm_version(algorithm_version_id)
        print("The response of AlgorithmVersionApi->get_algorithm_version:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AlgorithmVersionApi->get_algorithm_version: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **algorithm_version_id** | **str**|  | 

### Return type

[**ResultResponseAlgorithmVersionSchema**](ResultResponseAlgorithmVersionSchema.md)

### Authorization

[Auth0JWTBearer](../README.md#Auth0JWTBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_algorithm_versions**
> PaginatedResponseAlgorithmVersionSchema list_algorithm_versions(algorithm_id=algorithm_id)

List algorithm versions

Retrieve versions that are available for a given algorithm.

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.paginated_response_algorithm_version_schema import PaginatedResponseAlgorithmVersionSchema
from haplohub.rest import ApiException
from pprint import pprint

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: 
configuration = haplohub.Configuration(
    access_token=os.environ["API_KEY"]
)
# Enter a context with an instance of the API client
with haplohub.ApiClient(configuration) as api_client:
    algorithm_id = 'algorithm_id_example' # str |  (optional)

    try:
        # List algorithm versions
        api_response = api_client.algorithm_version_api.list_algorithm_versions(algorithm_id=algorithm_id)
        print("The response of AlgorithmVersionApi->list_algorithm_versions:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AlgorithmVersionApi->list_algorithm_versions: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **algorithm_id** | **str**|  | [optional] 

### Return type

[**PaginatedResponseAlgorithmVersionSchema**](PaginatedResponseAlgorithmVersionSchema.md)

### Authorization

[Auth0JWTBearer](../README.md#Auth0JWTBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


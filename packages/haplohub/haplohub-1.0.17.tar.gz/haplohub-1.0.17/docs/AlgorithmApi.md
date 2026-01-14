# haplohub.AlgorithmApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_algorithm**](AlgorithmApi.md#get_algorithm) | **GET** /api/v1/algorithm/{algorithm_id}/ | Get algorithm
[**list_algorithms**](AlgorithmApi.md#list_algorithms) | **GET** /api/v1/algorithm/ | List algorithms


# **get_algorithm**
> ResultResponseAlgorithmSchema get_algorithm(algorithm_id)

Get algorithm

Retrieve an algorithm definition by its identifier.

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.result_response_algorithm_schema import ResultResponseAlgorithmSchema
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
    algorithm_id = 'algorithm_id_example' # str | 

    try:
        # Get algorithm
        api_response = api_client.algorithm_api.get_algorithm(algorithm_id)
        print("The response of AlgorithmApi->get_algorithm:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AlgorithmApi->get_algorithm: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **algorithm_id** | **str**|  | 

### Return type

[**ResultResponseAlgorithmSchema**](ResultResponseAlgorithmSchema.md)

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

# **list_algorithms**
> PaginatedResponseAlgorithmSchema list_algorithms()

List algorithms

Retrieve algorithms that are available for execution.

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.paginated_response_algorithm_schema import PaginatedResponseAlgorithmSchema
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

    try:
        # List algorithms
        api_response = api_client.algorithm_api.list_algorithms()
        print("The response of AlgorithmApi->list_algorithms:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AlgorithmApi->list_algorithms: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

[**PaginatedResponseAlgorithmSchema**](PaginatedResponseAlgorithmSchema.md)

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


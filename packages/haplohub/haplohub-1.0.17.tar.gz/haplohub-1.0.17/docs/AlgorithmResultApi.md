# haplohub.AlgorithmResultApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_algorithm_result**](AlgorithmResultApi.md#create_algorithm_result) | **POST** /api/v1/algorithm-result/ | Create algorithm result
[**get_algorithm_result**](AlgorithmResultApi.md#get_algorithm_result) | **GET** /api/v1/algorithm-result/{algorithm_result_id}/ | Get algorithm result
[**list_algorithm_results**](AlgorithmResultApi.md#list_algorithm_results) | **GET** /api/v1/algorithm-result/ | List algorithm results


# **create_algorithm_result**
> ResultResponseAlgorithmResultSchema create_algorithm_result(create_algorithm_result_request)

Create algorithm result

Submit a request to execute an algorithm version.

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.create_algorithm_result_request import CreateAlgorithmResultRequest
from haplohub.models.result_response_algorithm_result_schema import ResultResponseAlgorithmResultSchema
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
    create_algorithm_result_request = haplohub.CreateAlgorithmResultRequest() # CreateAlgorithmResultRequest | 

    try:
        # Create algorithm result
        api_response = api_client.algorithm_result_api.create_algorithm_result(create_algorithm_result_request)
        print("The response of AlgorithmResultApi->create_algorithm_result:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AlgorithmResultApi->create_algorithm_result: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_algorithm_result_request** | [**CreateAlgorithmResultRequest**](CreateAlgorithmResultRequest.md)|  | 

### Return type

[**ResultResponseAlgorithmResultSchema**](ResultResponseAlgorithmResultSchema.md)

### Authorization

[Auth0JWTBearer](../README.md#Auth0JWTBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_algorithm_result**
> ResultResponseAlgorithmResultSchema get_algorithm_result(algorithm_result_id)

Get algorithm result

Retrieve an algorithm execution result by its identifier.

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.result_response_algorithm_result_schema import ResultResponseAlgorithmResultSchema
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
    algorithm_result_id = 'algorithm_result_id_example' # str | 

    try:
        # Get algorithm result
        api_response = api_client.algorithm_result_api.get_algorithm_result(algorithm_result_id)
        print("The response of AlgorithmResultApi->get_algorithm_result:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AlgorithmResultApi->get_algorithm_result: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **algorithm_result_id** | **str**|  | 

### Return type

[**ResultResponseAlgorithmResultSchema**](ResultResponseAlgorithmResultSchema.md)

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

# **list_algorithm_results**
> PaginatedResponseAlgorithmResultSchema list_algorithm_results(algorithm_version_id=algorithm_version_id, cohort_id=cohort_id)

List algorithm results

Retrieve algorithm execution results.

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.paginated_response_algorithm_result_schema import PaginatedResponseAlgorithmResultSchema
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
    algorithm_version_id = 'algorithm_version_id_example' # str |  (optional)
    cohort_id = 'cohort_id_example' # str |  (optional)

    try:
        # List algorithm results
        api_response = api_client.algorithm_result_api.list_algorithm_results(algorithm_version_id=algorithm_version_id, cohort_id=cohort_id)
        print("The response of AlgorithmResultApi->list_algorithm_results:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AlgorithmResultApi->list_algorithm_results: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **algorithm_version_id** | **str**|  | [optional] 
 **cohort_id** | **str**|  | [optional] 

### Return type

[**PaginatedResponseAlgorithmResultSchema**](PaginatedResponseAlgorithmResultSchema.md)

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


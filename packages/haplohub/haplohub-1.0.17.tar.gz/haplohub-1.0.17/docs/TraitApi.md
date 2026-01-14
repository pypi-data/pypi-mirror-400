# haplohub.TraitApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_trait**](TraitApi.md#get_trait) | **GET** /api/v1/trait/{trait_id}/ | Get trait
[**list_traits**](TraitApi.md#list_traits) | **GET** /api/v1/trait/ | List traits


# **get_trait**
> GetTraitResponse get_trait(trait_id)

Get trait

Retrieve a trait definition by its identifier.

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.get_trait_response import GetTraitResponse
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
    trait_id = 'trait_id_example' # str | 

    try:
        # Get trait
        api_response = api_client.trait_api.get_trait(trait_id)
        print("The response of TraitApi->get_trait:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TraitApi->get_trait: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **trait_id** | **str**|  | 

### Return type

[**GetTraitResponse**](GetTraitResponse.md)

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

# **list_traits**
> ListTraitsResponse list_traits(category_id=category_id, label=label)

List traits

Retrieve the catalog of traits that can be modeled.

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.list_traits_response import ListTraitsResponse
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
    category_id = 'category_id_example' # str |  (optional)
    label = 'label_example' # str |  (optional)

    try:
        # List traits
        api_response = api_client.trait_api.list_traits(category_id=category_id, label=label)
        print("The response of TraitApi->list_traits:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TraitApi->list_traits: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category_id** | **str**|  | [optional] 
 **label** | **str**|  | [optional] 

### Return type

[**ListTraitsResponse**](ListTraitsResponse.md)

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


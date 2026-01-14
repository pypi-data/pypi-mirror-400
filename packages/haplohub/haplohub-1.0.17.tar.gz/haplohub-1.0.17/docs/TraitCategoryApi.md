# haplohub.TraitCategoryApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_trait_category**](TraitCategoryApi.md#get_trait_category) | **GET** /api/v1/trait-category/{trait_category_id}/ | Get trait category
[**list_trait_categories**](TraitCategoryApi.md#list_trait_categories) | **GET** /api/v1/trait-category/ | List trait categories


# **get_trait_category**
> GetTraitCategoryResponse get_trait_category(trait_category_id)

Get trait category

Retrieve a trait category by its identifier.

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.get_trait_category_response import GetTraitCategoryResponse
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
    trait_category_id = 'trait_category_id_example' # str | 

    try:
        # Get trait category
        api_response = api_client.trait_category_api.get_trait_category(trait_category_id)
        print("The response of TraitCategoryApi->get_trait_category:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TraitCategoryApi->get_trait_category: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **trait_category_id** | **str**|  | 

### Return type

[**GetTraitCategoryResponse**](GetTraitCategoryResponse.md)

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

# **list_trait_categories**
> ListTraitCategoriesResponse list_trait_categories()

List trait categories

Retrieve the available categories that group related traits.

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.list_trait_categories_response import ListTraitCategoriesResponse
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
        # List trait categories
        api_response = api_client.trait_category_api.list_trait_categories()
        print("The response of TraitCategoryApi->list_trait_categories:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TraitCategoryApi->list_trait_categories: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

[**ListTraitCategoriesResponse**](ListTraitCategoriesResponse.md)

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


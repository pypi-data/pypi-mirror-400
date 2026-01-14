# haplohub.UserApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**haplohub_api_v1_user_check_slug**](UserApi.md#haplohub_api_v1_user_check_slug) | **POST** /api/v1/user/check-slug/ | Check Slug
[**haplohub_api_v1_user_get_user**](UserApi.md#haplohub_api_v1_user_get_user) | **GET** /api/v1/user/ | Get User
[**haplohub_api_v1_user_init_user**](UserApi.md#haplohub_api_v1_user_init_user) | **POST** /api/v1/user/init/ | Init User


# **haplohub_api_v1_user_check_slug**
> ResultResponseBool haplohub_api_v1_user_check_slug(check_slug_request)

Check Slug

### Example

```python
import time
import os
import haplohub
from haplohub.models.check_slug_request import CheckSlugRequest
from haplohub.models.result_response_bool import ResultResponseBool
from haplohub.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with haplohub.ApiClient(configuration) as api_client:
    check_slug_request = haplohub.CheckSlugRequest() # CheckSlugRequest | 

    try:
        # Check Slug
        api_response = api_client.user_api.haplohub_api_v1_user_check_slug(check_slug_request)
        print("The response of UserApi->haplohub_api_v1_user_check_slug:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UserApi->haplohub_api_v1_user_check_slug: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **check_slug_request** | [**CheckSlugRequest**](CheckSlugRequest.md)|  | 

### Return type

[**ResultResponseBool**](ResultResponseBool.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **haplohub_api_v1_user_get_user**
> ResultResponseUnionUserSchemaNoneType haplohub_api_v1_user_get_user()

Get User

### Example

```python
import time
import os
import haplohub
from haplohub.models.result_response_union_user_schema_none_type import ResultResponseUnionUserSchemaNoneType
from haplohub.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with haplohub.ApiClient(configuration) as api_client:

    try:
        # Get User
        api_response = api_client.user_api.haplohub_api_v1_user_get_user()
        print("The response of UserApi->haplohub_api_v1_user_get_user:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UserApi->haplohub_api_v1_user_get_user: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

[**ResultResponseUnionUserSchemaNoneType**](ResultResponseUnionUserSchemaNoneType.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **haplohub_api_v1_user_init_user**
> SuccessResponse haplohub_api_v1_user_init_user(init_user_request)

Init User

### Example

```python
import time
import os
import haplohub
from haplohub.models.init_user_request import InitUserRequest
from haplohub.models.success_response import SuccessResponse
from haplohub.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with haplohub.ApiClient(configuration) as api_client:
    init_user_request = haplohub.InitUserRequest() # InitUserRequest | 

    try:
        # Init User
        api_response = api_client.user_api.haplohub_api_v1_user_init_user(init_user_request)
        print("The response of UserApi->haplohub_api_v1_user_init_user:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UserApi->haplohub_api_v1_user_init_user: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **init_user_request** | [**InitUserRequest**](InitUserRequest.md)|  | 

### Return type

[**SuccessResponse**](SuccessResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Bad Request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


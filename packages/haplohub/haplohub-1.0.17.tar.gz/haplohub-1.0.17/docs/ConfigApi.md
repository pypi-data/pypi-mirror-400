# haplohub.ConfigApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**haplohub_api_v1_config_config**](ConfigApi.md#haplohub_api_v1_config_config) | **GET** /api/v1/config/ | Config


# **haplohub_api_v1_config_config**
> ResultResponseConfigSchema haplohub_api_v1_config_config()

Config

### Example

```python
import time
import os
import haplohub
from haplohub.models.result_response_config_schema import ResultResponseConfigSchema
from haplohub.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with haplohub.ApiClient(configuration) as api_client:

    try:
        # Config
        api_response = api_client.config_api.haplohub_api_v1_config_config()
        print("The response of ConfigApi->haplohub_api_v1_config_config:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConfigApi->haplohub_api_v1_config_config: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

[**ResultResponseConfigSchema**](ResultResponseConfigSchema.md)

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


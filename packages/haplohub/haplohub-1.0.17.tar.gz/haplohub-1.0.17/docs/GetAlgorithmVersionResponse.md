# GetAlgorithmVersionResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**AlgorithmVersionSchema**](AlgorithmVersionSchema.md) |  | 

## Example

```python
from haplohub.models.get_algorithm_version_response import GetAlgorithmVersionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetAlgorithmVersionResponse from a JSON string
get_algorithm_version_response_instance = GetAlgorithmVersionResponse.from_json(json)
# print the JSON string representation of the object
print GetAlgorithmVersionResponse.to_json()

# convert the object into a dict
get_algorithm_version_response_dict = get_algorithm_version_response_instance.to_dict()
# create an instance of GetAlgorithmVersionResponse from a dict
get_algorithm_version_response_from_dict = GetAlgorithmVersionResponse.from_dict(get_algorithm_version_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



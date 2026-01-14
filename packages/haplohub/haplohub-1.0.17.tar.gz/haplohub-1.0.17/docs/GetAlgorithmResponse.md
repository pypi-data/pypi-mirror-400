# GetAlgorithmResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**AlgorithmSchema**](AlgorithmSchema.md) |  | 

## Example

```python
from haplohub.models.get_algorithm_response import GetAlgorithmResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetAlgorithmResponse from a JSON string
get_algorithm_response_instance = GetAlgorithmResponse.from_json(json)
# print the JSON string representation of the object
print GetAlgorithmResponse.to_json()

# convert the object into a dict
get_algorithm_response_dict = get_algorithm_response_instance.to_dict()
# create an instance of GetAlgorithmResponse from a dict
get_algorithm_response_from_dict = GetAlgorithmResponse.from_dict(get_algorithm_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



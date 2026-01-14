# GetAlgorithmResultResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**AlgorithmResultSchema**](AlgorithmResultSchema.md) |  | 

## Example

```python
from haplohub.models.get_algorithm_result_response import GetAlgorithmResultResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetAlgorithmResultResponse from a JSON string
get_algorithm_result_response_instance = GetAlgorithmResultResponse.from_json(json)
# print the JSON string representation of the object
print GetAlgorithmResultResponse.to_json()

# convert the object into a dict
get_algorithm_result_response_dict = get_algorithm_result_response_instance.to_dict()
# create an instance of GetAlgorithmResultResponse from a dict
get_algorithm_result_response_from_dict = GetAlgorithmResultResponse.from_dict(get_algorithm_result_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



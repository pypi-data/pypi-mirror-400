# CreateAlgorithmResultResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**AlgorithmResultSchema**](AlgorithmResultSchema.md) |  | 

## Example

```python
from haplohub.models.create_algorithm_result_response import CreateAlgorithmResultResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateAlgorithmResultResponse from a JSON string
create_algorithm_result_response_instance = CreateAlgorithmResultResponse.from_json(json)
# print the JSON string representation of the object
print CreateAlgorithmResultResponse.to_json()

# convert the object into a dict
create_algorithm_result_response_dict = create_algorithm_result_response_instance.to_dict()
# create an instance of CreateAlgorithmResultResponse from a dict
create_algorithm_result_response_from_dict = CreateAlgorithmResultResponse.from_dict(create_algorithm_result_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



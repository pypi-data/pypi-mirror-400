# ListAlgorithmsResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**total_count** | **int** |  | 
**items** | [**List[AlgorithmSchema]**](AlgorithmSchema.md) |  | 

## Example

```python
from haplohub.models.list_algorithms_response import ListAlgorithmsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ListAlgorithmsResponse from a JSON string
list_algorithms_response_instance = ListAlgorithmsResponse.from_json(json)
# print the JSON string representation of the object
print ListAlgorithmsResponse.to_json()

# convert the object into a dict
list_algorithms_response_dict = list_algorithms_response_instance.to_dict()
# create an instance of ListAlgorithmsResponse from a dict
list_algorithms_response_from_dict = ListAlgorithmsResponse.from_dict(list_algorithms_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



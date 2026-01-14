# ListAlgorithmVersionsResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**total_count** | **int** |  | 
**items** | [**List[AlgorithmVersionSchema]**](AlgorithmVersionSchema.md) |  | 

## Example

```python
from haplohub.models.list_algorithm_versions_response import ListAlgorithmVersionsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ListAlgorithmVersionsResponse from a JSON string
list_algorithm_versions_response_instance = ListAlgorithmVersionsResponse.from_json(json)
# print the JSON string representation of the object
print ListAlgorithmVersionsResponse.to_json()

# convert the object into a dict
list_algorithm_versions_response_dict = list_algorithm_versions_response_instance.to_dict()
# create an instance of ListAlgorithmVersionsResponse from a dict
list_algorithm_versions_response_from_dict = ListAlgorithmVersionsResponse.from_dict(list_algorithm_versions_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



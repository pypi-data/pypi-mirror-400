# ListTraitsResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** |  | [optional] [default to 'success']
**total_count** | **int** |  | 
**items** | [**List[TraitSchema]**](TraitSchema.md) |  | 

## Example

```python
from haplohub.models.list_traits_response import ListTraitsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ListTraitsResponse from a JSON string
list_traits_response_instance = ListTraitsResponse.from_json(json)
# print the JSON string representation of the object
print ListTraitsResponse.to_json()

# convert the object into a dict
list_traits_response_dict = list_traits_response_instance.to_dict()
# create an instance of ListTraitsResponse from a dict
list_traits_response_from_dict = ListTraitsResponse.from_dict(list_traits_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



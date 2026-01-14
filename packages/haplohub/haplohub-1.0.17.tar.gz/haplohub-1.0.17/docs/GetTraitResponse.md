# GetTraitResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** |  | [optional] [default to 'success']
**result** | [**TraitSchema**](TraitSchema.md) |  | 

## Example

```python
from haplohub.models.get_trait_response import GetTraitResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetTraitResponse from a JSON string
get_trait_response_instance = GetTraitResponse.from_json(json)
# print the JSON string representation of the object
print GetTraitResponse.to_json()

# convert the object into a dict
get_trait_response_dict = get_trait_response_instance.to_dict()
# create an instance of GetTraitResponse from a dict
get_trait_response_from_dict = GetTraitResponse.from_dict(get_trait_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



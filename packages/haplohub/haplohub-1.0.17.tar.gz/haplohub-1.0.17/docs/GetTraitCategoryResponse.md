# GetTraitCategoryResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** |  | [optional] [default to 'success']
**result** | [**TraitCategorySchema**](TraitCategorySchema.md) |  | 

## Example

```python
from haplohub.models.get_trait_category_response import GetTraitCategoryResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetTraitCategoryResponse from a JSON string
get_trait_category_response_instance = GetTraitCategoryResponse.from_json(json)
# print the JSON string representation of the object
print GetTraitCategoryResponse.to_json()

# convert the object into a dict
get_trait_category_response_dict = get_trait_category_response_instance.to_dict()
# create an instance of GetTraitCategoryResponse from a dict
get_trait_category_response_from_dict = GetTraitCategoryResponse.from_dict(get_trait_category_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



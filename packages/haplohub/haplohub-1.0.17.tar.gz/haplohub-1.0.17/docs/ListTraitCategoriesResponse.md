# ListTraitCategoriesResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** |  | [optional] [default to 'success']
**total_count** | **int** |  | 
**items** | [**List[TraitCategorySchema]**](TraitCategorySchema.md) |  | 

## Example

```python
from haplohub.models.list_trait_categories_response import ListTraitCategoriesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ListTraitCategoriesResponse from a JSON string
list_trait_categories_response_instance = ListTraitCategoriesResponse.from_json(json)
# print the JSON string representation of the object
print ListTraitCategoriesResponse.to_json()

# convert the object into a dict
list_trait_categories_response_dict = list_trait_categories_response_instance.to_dict()
# create an instance of ListTraitCategoriesResponse from a dict
list_trait_categories_response_from_dict = ListTraitCategoriesResponse.from_dict(list_trait_categories_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



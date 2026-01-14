# TraitCategorySchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**label** | **str** |  | 

## Example

```python
from haplohub.models.trait_category_schema import TraitCategorySchema

# TODO update the JSON string below
json = "{}"
# create an instance of TraitCategorySchema from a JSON string
trait_category_schema_instance = TraitCategorySchema.from_json(json)
# print the JSON string representation of the object
print TraitCategorySchema.to_json()

# convert the object into a dict
trait_category_schema_dict = trait_category_schema_instance.to_dict()
# create an instance of TraitCategorySchema from a dict
trait_category_schema_from_dict = TraitCategorySchema.from_dict(trait_category_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



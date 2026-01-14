# TraitSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**label** | **str** |  | 
**category_id** | **str** |  | 
**ontology_url** | **str** |  | 

## Example

```python
from haplohub.models.trait_schema import TraitSchema

# TODO update the JSON string below
json = "{}"
# create an instance of TraitSchema from a JSON string
trait_schema_instance = TraitSchema.from_json(json)
# print the JSON string representation of the object
print TraitSchema.to_json()

# convert the object into a dict
trait_schema_dict = trait_schema_instance.to_dict()
# create an instance of TraitSchema from a dict
trait_schema_from_dict = TraitSchema.from_dict(trait_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



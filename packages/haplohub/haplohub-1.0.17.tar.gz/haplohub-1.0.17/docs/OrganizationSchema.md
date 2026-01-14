# OrganizationSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**name** | **str** |  | 
**display_name** | **str** |  | 

## Example

```python
from haplohub.models.organization_schema import OrganizationSchema

# TODO update the JSON string below
json = "{}"
# create an instance of OrganizationSchema from a JSON string
organization_schema_instance = OrganizationSchema.from_json(json)
# print the JSON string representation of the object
print OrganizationSchema.to_json()

# convert the object into a dict
organization_schema_dict = organization_schema_instance.to_dict()
# create an instance of OrganizationSchema from a dict
organization_schema_from_dict = OrganizationSchema.from_dict(organization_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



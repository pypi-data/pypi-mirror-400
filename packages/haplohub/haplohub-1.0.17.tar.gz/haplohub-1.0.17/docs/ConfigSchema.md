# ConfigSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cli** | [**CliSchema**](CliSchema.md) |  | 

## Example

```python
from haplohub.models.config_schema import ConfigSchema

# TODO update the JSON string below
json = "{}"
# create an instance of ConfigSchema from a JSON string
config_schema_instance = ConfigSchema.from_json(json)
# print the JSON string representation of the object
print ConfigSchema.to_json()

# convert the object into a dict
config_schema_dict = config_schema_instance.to_dict()
# create an instance of ConfigSchema from a dict
config_schema_from_dict = ConfigSchema.from_dict(config_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



# CliSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**auth_domain** | **str** |  | 
**auth_client_id** | **str** |  | 
**auth_audience** | **str** |  | 

## Example

```python
from haplohub.models.cli_schema import CliSchema

# TODO update the JSON string below
json = "{}"
# create an instance of CliSchema from a JSON string
cli_schema_instance = CliSchema.from_json(json)
# print the JSON string representation of the object
print CliSchema.to_json()

# convert the object into a dict
cli_schema_dict = cli_schema_instance.to_dict()
# create an instance of CliSchema from a dict
cli_schema_from_dict = CliSchema.from_dict(cli_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



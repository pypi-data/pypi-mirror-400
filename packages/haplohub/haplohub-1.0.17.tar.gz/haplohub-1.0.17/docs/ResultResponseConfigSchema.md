# ResultResponseConfigSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** |  | [optional] [default to 'success']
**result** | [**ConfigSchema**](ConfigSchema.md) |  | 

## Example

```python
from haplohub.models.result_response_config_schema import ResultResponseConfigSchema

# TODO update the JSON string below
json = "{}"
# create an instance of ResultResponseConfigSchema from a JSON string
result_response_config_schema_instance = ResultResponseConfigSchema.from_json(json)
# print the JSON string representation of the object
print ResultResponseConfigSchema.to_json()

# convert the object into a dict
result_response_config_schema_dict = result_response_config_schema_instance.to_dict()
# create an instance of ResultResponseConfigSchema from a dict
result_response_config_schema_from_dict = ResultResponseConfigSchema.from_dict(result_response_config_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



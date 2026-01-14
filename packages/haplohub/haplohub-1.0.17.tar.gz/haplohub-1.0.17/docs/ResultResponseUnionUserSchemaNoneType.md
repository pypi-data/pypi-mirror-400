# ResultResponseUnionUserSchemaNoneType


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** |  | [optional] [default to 'success']
**result** | [**UserSchema**](UserSchema.md) |  | 

## Example

```python
from haplohub.models.result_response_union_user_schema_none_type import ResultResponseUnionUserSchemaNoneType

# TODO update the JSON string below
json = "{}"
# create an instance of ResultResponseUnionUserSchemaNoneType from a JSON string
result_response_union_user_schema_none_type_instance = ResultResponseUnionUserSchemaNoneType.from_json(json)
# print the JSON string representation of the object
print ResultResponseUnionUserSchemaNoneType.to_json()

# convert the object into a dict
result_response_union_user_schema_none_type_dict = result_response_union_user_schema_none_type_instance.to_dict()
# create an instance of ResultResponseUnionUserSchemaNoneType from a dict
result_response_union_user_schema_none_type_from_dict = ResultResponseUnionUserSchemaNoneType.from_dict(result_response_union_user_schema_none_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



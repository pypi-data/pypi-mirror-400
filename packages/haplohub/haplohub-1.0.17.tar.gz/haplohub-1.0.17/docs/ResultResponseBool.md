# ResultResponseBool


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** |  | [optional] [default to 'success']
**result** | **bool** |  | 

## Example

```python
from haplohub.models.result_response_bool import ResultResponseBool

# TODO update the JSON string below
json = "{}"
# create an instance of ResultResponseBool from a JSON string
result_response_bool_instance = ResultResponseBool.from_json(json)
# print the JSON string representation of the object
print ResultResponseBool.to_json()

# convert the object into a dict
result_response_bool_dict = result_response_bool_instance.to_dict()
# create an instance of ResultResponseBool from a dict
result_response_bool_from_dict = ResultResponseBool.from_dict(result_response_bool_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



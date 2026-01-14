# ResultResponseAlgorithmVersionSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** |  | [optional] [default to 'success']
**result** | [**AlgorithmVersionSchema**](AlgorithmVersionSchema.md) |  | 

## Example

```python
from haplohub.models.result_response_algorithm_version_schema import ResultResponseAlgorithmVersionSchema

# TODO update the JSON string below
json = "{}"
# create an instance of ResultResponseAlgorithmVersionSchema from a JSON string
result_response_algorithm_version_schema_instance = ResultResponseAlgorithmVersionSchema.from_json(json)
# print the JSON string representation of the object
print ResultResponseAlgorithmVersionSchema.to_json()

# convert the object into a dict
result_response_algorithm_version_schema_dict = result_response_algorithm_version_schema_instance.to_dict()
# create an instance of ResultResponseAlgorithmVersionSchema from a dict
result_response_algorithm_version_schema_from_dict = ResultResponseAlgorithmVersionSchema.from_dict(result_response_algorithm_version_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



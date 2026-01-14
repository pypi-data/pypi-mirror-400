# AlgorithmVersionSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**algorithm_id** | **str** |  | 
**version** | **str** |  | 
**openapi_schema** | **object** |  | 
**modified** | **datetime** |  | [optional] 
**created** | **datetime** |  | [optional] 

## Example

```python
from haplohub.models.algorithm_version_schema import AlgorithmVersionSchema

# TODO update the JSON string below
json = "{}"
# create an instance of AlgorithmVersionSchema from a JSON string
algorithm_version_schema_instance = AlgorithmVersionSchema.from_json(json)
# print the JSON string representation of the object
print AlgorithmVersionSchema.to_json()

# convert the object into a dict
algorithm_version_schema_dict = algorithm_version_schema_instance.to_dict()
# create an instance of AlgorithmVersionSchema from a dict
algorithm_version_schema_from_dict = AlgorithmVersionSchema.from_dict(algorithm_version_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



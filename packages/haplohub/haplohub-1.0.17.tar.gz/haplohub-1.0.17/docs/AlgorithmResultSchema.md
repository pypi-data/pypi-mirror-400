# AlgorithmResultSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**algorithm_version_id** | **str** |  | 
**cohort_id** | **str** |  | 
**input** | **object** |  | 
**output** | **object** |  | [optional] 
**status** | **str** |  | [optional] [default to 'Pending']
**modified** | **datetime** |  | [optional] 
**created** | **datetime** |  | [optional] 

## Example

```python
from haplohub.models.algorithm_result_schema import AlgorithmResultSchema

# TODO update the JSON string below
json = "{}"
# create an instance of AlgorithmResultSchema from a JSON string
algorithm_result_schema_instance = AlgorithmResultSchema.from_json(json)
# print the JSON string representation of the object
print AlgorithmResultSchema.to_json()

# convert the object into a dict
algorithm_result_schema_dict = algorithm_result_schema_instance.to_dict()
# create an instance of AlgorithmResultSchema from a dict
algorithm_result_schema_from_dict = AlgorithmResultSchema.from_dict(algorithm_result_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



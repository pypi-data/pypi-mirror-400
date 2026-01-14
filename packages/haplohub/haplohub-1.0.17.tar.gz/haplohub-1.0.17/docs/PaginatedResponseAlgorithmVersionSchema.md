# PaginatedResponseAlgorithmVersionSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** |  | [optional] [default to 'success']
**total_count** | **int** |  | 
**items** | [**List[AlgorithmVersionSchema]**](AlgorithmVersionSchema.md) |  | 

## Example

```python
from haplohub.models.paginated_response_algorithm_version_schema import PaginatedResponseAlgorithmVersionSchema

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResponseAlgorithmVersionSchema from a JSON string
paginated_response_algorithm_version_schema_instance = PaginatedResponseAlgorithmVersionSchema.from_json(json)
# print the JSON string representation of the object
print PaginatedResponseAlgorithmVersionSchema.to_json()

# convert the object into a dict
paginated_response_algorithm_version_schema_dict = paginated_response_algorithm_version_schema_instance.to_dict()
# create an instance of PaginatedResponseAlgorithmVersionSchema from a dict
paginated_response_algorithm_version_schema_from_dict = PaginatedResponseAlgorithmVersionSchema.from_dict(paginated_response_algorithm_version_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



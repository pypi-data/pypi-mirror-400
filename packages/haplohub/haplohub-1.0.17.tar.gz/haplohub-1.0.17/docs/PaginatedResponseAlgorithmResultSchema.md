# PaginatedResponseAlgorithmResultSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** |  | [optional] [default to 'success']
**total_count** | **int** |  | 
**items** | [**List[AlgorithmResultSchema]**](AlgorithmResultSchema.md) |  | 

## Example

```python
from haplohub.models.paginated_response_algorithm_result_schema import PaginatedResponseAlgorithmResultSchema

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResponseAlgorithmResultSchema from a JSON string
paginated_response_algorithm_result_schema_instance = PaginatedResponseAlgorithmResultSchema.from_json(json)
# print the JSON string representation of the object
print PaginatedResponseAlgorithmResultSchema.to_json()

# convert the object into a dict
paginated_response_algorithm_result_schema_dict = paginated_response_algorithm_result_schema_instance.to_dict()
# create an instance of PaginatedResponseAlgorithmResultSchema from a dict
paginated_response_algorithm_result_schema_from_dict = PaginatedResponseAlgorithmResultSchema.from_dict(paginated_response_algorithm_result_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



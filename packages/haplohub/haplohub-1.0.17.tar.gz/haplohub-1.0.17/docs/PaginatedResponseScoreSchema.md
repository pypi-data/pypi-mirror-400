# PaginatedResponseScoreSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** |  | [optional] [default to 'success']
**total_count** | **int** |  | 
**items** | [**List[ScoreSchema]**](ScoreSchema.md) |  | 

## Example

```python
from haplohub.models.paginated_response_score_schema import PaginatedResponseScoreSchema

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResponseScoreSchema from a JSON string
paginated_response_score_schema_instance = PaginatedResponseScoreSchema.from_json(json)
# print the JSON string representation of the object
print PaginatedResponseScoreSchema.to_json()

# convert the object into a dict
paginated_response_score_schema_dict = paginated_response_score_schema_instance.to_dict()
# create an instance of PaginatedResponseScoreSchema from a dict
paginated_response_score_schema_from_dict = PaginatedResponseScoreSchema.from_dict(paginated_response_score_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



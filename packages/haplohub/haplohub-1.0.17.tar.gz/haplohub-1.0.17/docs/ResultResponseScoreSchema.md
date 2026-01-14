# ResultResponseScoreSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** |  | [optional] [default to 'success']
**result** | [**ScoreSchema**](ScoreSchema.md) |  | 

## Example

```python
from haplohub.models.result_response_score_schema import ResultResponseScoreSchema

# TODO update the JSON string below
json = "{}"
# create an instance of ResultResponseScoreSchema from a JSON string
result_response_score_schema_instance = ResultResponseScoreSchema.from_json(json)
# print the JSON string representation of the object
print ResultResponseScoreSchema.to_json()

# convert the object into a dict
result_response_score_schema_dict = result_response_score_schema_instance.to_dict()
# create an instance of ResultResponseScoreSchema from a dict
result_response_score_schema_from_dict = ResultResponseScoreSchema.from_dict(result_response_score_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



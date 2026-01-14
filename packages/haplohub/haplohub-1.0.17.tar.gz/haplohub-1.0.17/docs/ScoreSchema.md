# ScoreSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**member_id** | **str** |  | 
**sample_id** | **str** |  | 
**result_id** | **str** |  | 
**pgs_model_id** | **str** |  | 
**adjusted_z_score** | **float** |  | 
**percentile** | **float** |  | 
**population_id** | **str** |  | 
**population_percentile** | **float** |  | 
**population_z_score** | **float** |  | 
**modified** | **datetime** |  | [optional] 
**created** | **datetime** |  | [optional] 

## Example

```python
from haplohub.models.score_schema import ScoreSchema

# TODO update the JSON string below
json = "{}"
# create an instance of ScoreSchema from a JSON string
score_schema_instance = ScoreSchema.from_json(json)
# print the JSON string representation of the object
print ScoreSchema.to_json()

# convert the object into a dict
score_schema_dict = score_schema_instance.to_dict()
# create an instance of ScoreSchema from a dict
score_schema_from_dict = ScoreSchema.from_dict(score_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



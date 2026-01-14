# MemberPgsScoreSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**cohort_id** | **str** |  | 
**member_id** | **str** |  | 
**trait_id** | **str** |  | 
**adjusted_z_score** | **float** |  | 
**percentile** | **float** |  | 
**relative_risk** | **float** |  | [optional] 
**most_similar_population** | [**MostSimilarPopulation**](MostSimilarPopulation.md) |  | 
**source_algorithm_result_id** | **str** |  | 
**time_created** | **datetime** |  | 

## Example

```python
from haplohub.models.member_pgs_score_schema import MemberPgsScoreSchema

# TODO update the JSON string below
json = "{}"
# create an instance of MemberPgsScoreSchema from a JSON string
member_pgs_score_schema_instance = MemberPgsScoreSchema.from_json(json)
# print the JSON string representation of the object
print MemberPgsScoreSchema.to_json()

# convert the object into a dict
member_pgs_score_schema_dict = member_pgs_score_schema_instance.to_dict()
# create an instance of MemberPgsScoreSchema from a dict
member_pgs_score_schema_from_dict = MemberPgsScoreSchema.from_dict(member_pgs_score_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



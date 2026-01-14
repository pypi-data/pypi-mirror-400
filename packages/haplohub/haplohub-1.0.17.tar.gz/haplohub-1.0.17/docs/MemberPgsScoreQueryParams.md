# MemberPgsScoreQueryParams


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**member_id** | **str** |  | 
**latest** | **bool** |  | [optional] [default to False]

## Example

```python
from haplohub.models.member_pgs_score_query_params import MemberPgsScoreQueryParams

# TODO update the JSON string below
json = "{}"
# create an instance of MemberPgsScoreQueryParams from a JSON string
member_pgs_score_query_params_instance = MemberPgsScoreQueryParams.from_json(json)
# print the JSON string representation of the object
print MemberPgsScoreQueryParams.to_json()

# convert the object into a dict
member_pgs_score_query_params_dict = member_pgs_score_query_params_instance.to_dict()
# create an instance of MemberPgsScoreQueryParams from a dict
member_pgs_score_query_params_from_dict = MemberPgsScoreQueryParams.from_dict(member_pgs_score_query_params_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



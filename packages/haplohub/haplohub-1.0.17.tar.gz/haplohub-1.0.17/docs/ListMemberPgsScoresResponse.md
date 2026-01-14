# ListMemberPgsScoresResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**total_count** | **int** |  | 
**items** | [**List[MemberPgsScoreSchema]**](MemberPgsScoreSchema.md) |  | 

## Example

```python
from haplohub.models.list_member_pgs_scores_response import ListMemberPgsScoresResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ListMemberPgsScoresResponse from a JSON string
list_member_pgs_scores_response_instance = ListMemberPgsScoresResponse.from_json(json)
# print the JSON string representation of the object
print ListMemberPgsScoresResponse.to_json()

# convert the object into a dict
list_member_pgs_scores_response_dict = list_member_pgs_scores_response_instance.to_dict()
# create an instance of ListMemberPgsScoresResponse from a dict
list_member_pgs_scores_response_from_dict = ListMemberPgsScoresResponse.from_dict(list_member_pgs_scores_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



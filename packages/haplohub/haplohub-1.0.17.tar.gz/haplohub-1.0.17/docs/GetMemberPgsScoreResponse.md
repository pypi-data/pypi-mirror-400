# GetMemberPgsScoreResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ResponseStatus**](ResponseStatus.md) |  | [optional] 
**result** | [**MemberPgsScoreSchema**](MemberPgsScoreSchema.md) |  | 

## Example

```python
from haplohub.models.get_member_pgs_score_response import GetMemberPgsScoreResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetMemberPgsScoreResponse from a JSON string
get_member_pgs_score_response_instance = GetMemberPgsScoreResponse.from_json(json)
# print the JSON string representation of the object
print GetMemberPgsScoreResponse.to_json()

# convert the object into a dict
get_member_pgs_score_response_dict = get_member_pgs_score_response_instance.to_dict()
# create an instance of GetMemberPgsScoreResponse from a dict
get_member_pgs_score_response_from_dict = GetMemberPgsScoreResponse.from_dict(get_member_pgs_score_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



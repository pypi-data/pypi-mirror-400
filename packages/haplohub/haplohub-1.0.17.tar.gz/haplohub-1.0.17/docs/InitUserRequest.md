# InitUserRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**full_name** | **str** |  | 
**email** | **str** |  | 
**organization_slug** | **str** |  | 
**organization_display_name** | **str** |  | 

## Example

```python
from haplohub.models.init_user_request import InitUserRequest

# TODO update the JSON string below
json = "{}"
# create an instance of InitUserRequest from a JSON string
init_user_request_instance = InitUserRequest.from_json(json)
# print the JSON string representation of the object
print InitUserRequest.to_json()

# convert the object into a dict
init_user_request_dict = init_user_request_instance.to_dict()
# create an instance of InitUserRequest from a dict
init_user_request_from_dict = InitUserRequest.from_dict(init_user_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



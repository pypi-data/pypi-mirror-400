# CreateAlgorithmResultRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**algorithm_version_id** | **str** |  | 
**cohort_id** | **str** |  | 
**input** | **object** |  | 

## Example

```python
from haplohub.models.create_algorithm_result_request import CreateAlgorithmResultRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateAlgorithmResultRequest from a JSON string
create_algorithm_result_request_instance = CreateAlgorithmResultRequest.from_json(json)
# print the JSON string representation of the object
print CreateAlgorithmResultRequest.to_json()

# convert the object into a dict
create_algorithm_result_request_dict = create_algorithm_result_request_instance.to_dict()
# create an instance of CreateAlgorithmResultRequest from a dict
create_algorithm_result_request_from_dict = CreateAlgorithmResultRequest.from_dict(create_algorithm_result_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



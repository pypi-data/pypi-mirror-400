# ReportTemplateListSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**name** | **str** |  | 
**description** | **str** |  | [optional] [default to '']
**report_type** | **str** |  | [optional] [default to 'text']
**created** | **datetime** |  | [optional] 
**modified** | **datetime** |  | [optional] 

## Example

```python
from haplohub.models.report_template_list_schema import ReportTemplateListSchema

# TODO update the JSON string below
json = "{}"
# create an instance of ReportTemplateListSchema from a JSON string
report_template_list_schema_instance = ReportTemplateListSchema.from_json(json)
# print the JSON string representation of the object
print ReportTemplateListSchema.to_json()

# convert the object into a dict
report_template_list_schema_dict = report_template_list_schema_instance.to_dict()
# create an instance of ReportTemplateListSchema from a dict
report_template_list_schema_from_dict = ReportTemplateListSchema.from_dict(report_template_list_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



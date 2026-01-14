# PaginatedResponseReportTemplateListSchema


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** |  | [optional] [default to 'success']
**total_count** | **int** |  | 
**items** | [**List[ReportTemplateListSchema]**](ReportTemplateListSchema.md) |  | 

## Example

```python
from haplohub.models.paginated_response_report_template_list_schema import PaginatedResponseReportTemplateListSchema

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResponseReportTemplateListSchema from a JSON string
paginated_response_report_template_list_schema_instance = PaginatedResponseReportTemplateListSchema.from_json(json)
# print the JSON string representation of the object
print PaginatedResponseReportTemplateListSchema.to_json()

# convert the object into a dict
paginated_response_report_template_list_schema_dict = paginated_response_report_template_list_schema_instance.to_dict()
# create an instance of PaginatedResponseReportTemplateListSchema from a dict
paginated_response_report_template_list_schema_from_dict = PaginatedResponseReportTemplateListSchema.from_dict(paginated_response_report_template_list_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



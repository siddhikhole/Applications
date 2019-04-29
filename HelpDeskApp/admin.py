from django.contrib import admin
from .models import HelpdeskRequestSLAs,WorkflowRequest,EmployeeMaster,AppList,HelpdeskCategories,HelpdeskOfficeLocation,HelpdeskConfigurationMaster,HelpdeskDepartments,Categories,sub_categories,HelpdeskFulfillerGroups,HelpdeskExpectedClosureDetails,HelpRequest,Workflow_email_templates
# Register your models here.


admin.site.register(EmployeeMaster)
admin.site.register(AppList)
admin.site.register(HelpdeskCategories)
admin.site.register(HelpdeskDepartments)
admin.site.register(HelpRequest)
admin.site.register(HelpdeskConfigurationMaster)
admin.site.register(HelpdeskOfficeLocation)
admin.site.register(HelpdeskExpectedClosureDetails)
admin.site.register(Categories)
admin.site.register(sub_categories)
admin.site.register(Workflow_email_templates)
admin.site.register(WorkflowRequest)
admin.site.register(HelpdeskRequestSLAs)
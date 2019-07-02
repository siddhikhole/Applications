from django.db import models


class EmployeeMaster(models.Model):
	empid = models.CharField(max_length=20, null=True)
	new_emp_id = models.CharField(max_length=20, null=True)
	salutation = models.CharField(max_length=4, null=True)
	name1 = models.CharField(max_length=50, null=True)
	name2 = models.CharField(max_length=50, null=True)
	name3 = models.CharField(max_length=50, null=True)
	date_of_Joining = models.DateField(default=None, null=True)
	associated_user_account = models.CharField(max_length=100, null=True)
	email = models.CharField(max_length=100, unique=True, null=True)
	reporting_to_designation = models.CharField(max_length=100, null=True)
	reporting_to = models.CharField(max_length=100, null=True)
	emp_hd = models.CharField(max_length=100, null=True)
	employee_status = models.CharField(max_length=100, null=True)
	employment_status = models.CharField(max_length=100, null=True)
	confirmationDate = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
	department = models.CharField(max_length=100, null=True)
	position = models.CharField(max_length=100, null=True)
	grade = models.CharField(max_length=100, null=True)
	performance_group = models.CharField(max_length=100, null=True)
	role = models.CharField(max_length=100, null=True)
	cost_center = models.CharField(max_length=100, null=True)
	employment_type = models.CharField(max_length=100, null=True)
	employment_segment = models.CharField(max_length=100, null=True)
	service_agreement_end_date = models.DateField(default=None, null=True)
	service_agreement_start_date = models.DateField(default=None, null=True)
	base_location = models.CharField(max_length=100, null=True)
	base_zone = models.CharField(max_length=100, null=True)
	base_state = models.CharField(max_length=100, null=True)
	base_city = models.CharField(max_length=100, null=True)
	base_address1 = models.CharField(max_length=1000, null=True)
	base_address2 = models.CharField(max_length=1000, null=True)
	date_Of_leaving = models.DateField(default=None, null=True)
	current_location = models.CharField(max_length=1000, null=True)
	date_of_separation = models.DateField(default=None, null=True)
	current_zone = models.CharField(max_length=1000, null=True)
	current_state = models.CharField(max_length=1000, null=True)
	current_city = models.CharField(max_length=100, null=True)
	current_address1 = models.CharField(max_length=1000, null=True)
	current_zip_code = models.CharField(max_length=1000, null=True)
	source_of_joining = models.CharField(max_length=1000, null=True)
	base_zip_code = models.CharField(max_length=100, null=True)
	sub_department = models.CharField(max_length=100, null=True)
	in_active = models.BooleanField(default=True, null=True)
	id = models.AutoField(primary_key=True)
	created_by = models.CharField(max_length=100, null=True)
	modified_by = models.CharField(max_length=100, null=True)
	modified = models.DateField(default=None, null=True)
	created = models.DateField(auto_now_add=True, auto_now=False, null=True)
	location = models.CharField(max_length=100, null=True)
	appraiser = models.CharField(max_length=100, null=True)
	reviewer = models.CharField(max_length=100, null=True)
	item_type = models.CharField(max_length=100, null=True)
	path = models.CharField(max_length=100, default=None, null=True)


class AppList(models.Model):
	title = models.CharField(max_length=100, default=None, null=True)
	apps_list_id = models.IntegerField(null=True)
	user = models.CharField(max_length=100, null=True)
	roles = models.CharField(max_length=100, null=True)
	original_created_by = models.CharField(max_length=100, null=True)
	original_modified_by = models.CharField(max_length=100, null=True)
	in_active = models.BooleanField(default=False, null=True)
	designation = models.CharField(max_length=100, null=True)
	item_type = models.CharField(max_length=100, null=True)
	path = models.CharField(max_length=100, default=None, null=True)


class HelpdeskCategories(models.Model):
	title = models.CharField(max_length=100, null=True)
	category = models.CharField(max_length=100, null=True)
	in_active = models.BooleanField(default=False, null=True)
	request_type = models.CharField(max_length=100, null=True, default="Request")
	location = models.CharField(max_length=100, null=True)
	department = models.CharField(max_length=100, null=True)
	item_type = models.CharField(max_length=100, null=True)
	path = models.CharField(max_length=100, default=None, null=True)


class HelpdeskOfficeLocation(models.Model):
	title = models.CharField(max_length=100, null=True)
	item_type = models.CharField(max_length=100, null=True)
	path = models.CharField(max_length=100, default=None, null=True)


class HelpdeskConfigurationMaster(models.Model):
	title = models.CharField(max_length=100, null=True)
	item_value = models.CharField(max_length=100, null=True)
	item_type = models.CharField(max_length=100, null=True)
	path = models.CharField(max_length=100, default=None, null=True)


class HelpdeskDepartments(models.Model):
	title = models.CharField(max_length=100, null=True)
	request_type = models.CharField(max_length=100, null=True)
	department = models.CharField(max_length=100, null=True)
	item_type = models.CharField(max_length=100, null=True)
	path = models.CharField(max_length=100, default=None, null=True)


class Categories(models.Model):
	title = models.CharField(max_length=500)
	department_id = models.ForeignKey(HelpdeskDepartments, on_delete=models.CASCADE)


class sub_categories(models.Model):
	title = models.CharField(max_length=500)
	department_id = models.ForeignKey(Categories, on_delete=models.CASCADE)


class HelpdeskFulfillerGroups(models.Model):
	title = models.CharField(max_length=100, null=True)
	group_name = models.CharField(max_length=100, null=True)
	employee_id = models.CharField(max_length=100, null=True)
	employee_name = models.CharField(max_length=100, null=True)
	role_name = models.CharField(max_length=100, null=True)
	item_type = models.CharField(max_length=100, null=True)
	path = models.CharField(max_length=100, default=None, null=True)


class HelpdeskExpectedClosureDetails(models.Model):
	title = models.CharField(max_length=100, null=True)
	start_hour = models.IntegerField(null=True)
	hours_per_day = models.IntegerField(null=True)
	holiday = models.IntegerField(null=True)
	item_type = models.CharField(max_length=100, null=True)
	path = models.CharField(max_length=100, default=None, null=True)


class Workflow_email_templates(models.Model):
	key = models.CharField(max_length=1000, null=True)
	process = models.TextField(max_length=1000, null=True)
	template_body = models.TextField(null=True)
	template_subject = models.TextField(null=True)


class HelpRequest(models.Model):
	created_at = models.DateTimeField(default=None, null=True)
	description = models.CharField(max_length=1000, null=True)
	request_type = models.CharField(max_length=50, null=True)
	department = models.CharField(max_length=50, null=True)
	category = models.CharField(max_length=1000, null=True)
	sub_category = models.CharField(max_length=1000, null=True)
	location = models.CharField(max_length=1000, null=True)
	priority = models.CharField(max_length=1000, null=True)
	expected_closure = models.CharField(max_length=1000, null=True)
	ticket_for = models.CharField(max_length=100, null=True, default="Self")
	employee_id = models.CharField(max_length=100, null=True)
	EmployeeName = models.CharField(max_length=100, null=True)
	OnBehalfUser = models.CharField(max_length=100, null=True)
	OnBehalfUserEmployeeId = models.CharField(max_length=100, null=True)
	OnBehalfUserEmployeeName = models.CharField(max_length=100, null=True)
	FirstLevelApproverEmployeeId = models.CharField(max_length=100, null=True)
	FirstLevelApproverEmployeeName = models.CharField(max_length=100, null=True)
	SecondLevelApproverEmployeeId = models.CharField(max_length=100, null=True)
	SecondLevelApproverEmployeeName = models.CharField(max_length=100, null=True)
	FulfillerHead = models.CharField(max_length=100, null=True)
	AutomaticFulfillerAssignment = models.CharField(max_length=100, null=True)
	FulfillerExecutive = models.CharField(max_length=100, null=True)
	ReferenceTicketNo = models.CharField(max_length=100, null=True)
	RequestStatus = models.CharField(max_length=100, null=True)
	WorkflowStatus = models.CharField(max_length=100, null=True, default="Pending")
	WorkflowCurrentStatus = models.CharField(max_length=100, null=True, default="Workflow Initiated")
	WorkflowOverallStatus = models.CharField(max_length=100, null=True)
	WorkflowCurrentActor = models.CharField(max_length=100, null=True)
	WorkflowModifiedOn = models.DateTimeField(default=None, null=True)
	InActive = models.CharField(max_length=20, default=True, null=True)
	Files = models.FileField(upload_to="Documents", default="media/Documents/no-image.jpg", null=True)
	FulfillmentCompletedDate = models.DateTimeField(default=None, null=True)
	HelpdeskOffice = models.CharField(max_length=100, null=True)
	DeskLocation = models.CharField(max_length=100, null=True)


class WorkflowRequest(models.Model):
	ActedByUser = models.CharField(max_length=100, null=True)
	ActedOn = models.DateTimeField(null=True)
	Action = models.CharField(max_length=100, null=True)
	ActionData = models.CharField(max_length=100, null=True)
	Actor = models.CharField(max_length=100, null=True)
	Process = models.CharField(max_length=100, null=True)
	RequestID = models.ForeignKey(HelpRequest, on_delete=models.CASCADE)
	RequestStatus = models.CharField(max_length=100, null=True)
	SchemaName = models.CharField(max_length=100, null=True)
	WorkflowPendingWith = models.CharField(max_length=100, null=True)


class HelpdeskRequestSLAs(models.Model):
	EM_0_AfterHrs = models.IntegerField(null=True)
	EM_0_AfterMin = models.IntegerField(null=True)
	EM_0_Name = models.CharField(null=True, max_length=100)
	EM_0_To = models.CharField(null=True, max_length=100)
	EM_1_AfterHrs = models.IntegerField(null=True)
	EM_1_AfterMin = models.IntegerField(null=True)
	EM_1_Name = models.CharField(null=True, max_length=100)
	EM_1_To = models.CharField(null=True, max_length=100)
	EM_2_AfterHrs = models.IntegerField(null=True)
	EM_2_AfterMin = models.IntegerField(null=True)
	EM_2_Name = models.CharField(null=True, max_length=100)
	EM_2_To = models.CharField(null=True, max_length=100)
	FulfillerExecutive = models.CharField(null=True, max_length=100)
	HelpdeskCategory = models.CharField(null=True, max_length=100)
	HelpdeskDepartment = models.CharField(null=True, max_length=100)
	HelpdeskLocation = models.CharField(null=True, max_length=100)
	HelpdeskPriority = models.CharField(null=True, max_length=100)
	HelpdeskSubCategory = models.CharField(null=True, max_length=100)
	ReminderMechanism = models.CharField(null=True, max_length=100)
	TATHrs = models.IntegerField(null=True)
	TATMins = models.IntegerField(null=True)

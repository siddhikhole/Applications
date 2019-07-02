def get_users(all_items):
	total = {}
	for work in all_items:
		total[work.id] = {
			"EmployeeName": work.EmployeeName,
			"id": work.id,
			"created_at": work.created_at,
			"department": work.department,
			"category": work.category,
			"sub_category": work.sub_category,
			"WorkflowCurrentStatus": work.WorkflowCurrentStatus
		}
	return total

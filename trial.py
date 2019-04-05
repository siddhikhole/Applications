lines = []
while True:
	try:
		line = input()
		lines.append(line)
		text = '\n'.join(lines)
	except:
		text_file = open("Output.txt", "w")
		text_file.write("Content:\n"+str(text))
		text_file.close()
		break
workflow=WorkflowRequest.objects.get(RequestID_id=ticket_id,RequestStatus="Pending")
		print(workflow.WorkflowPendingWith)

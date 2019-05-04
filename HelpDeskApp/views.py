import threading
import datetime
from datetime import timedelta
import dateutil.parser
from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.db.models import Q
from django.core.mail import send_mail,EmailMessage,EmailMultiAlternatives
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
import numpy as np
from HelpDeskApp.authhelper import get_signin_url,get_token_from_code 	
from HelpDeskApp.outlookservice import get_me
from HelpDeskApp.email import send_html_mail 
from .models import WorkflowRequest,HelpdeskRequestSLAs,EmployeeMaster,AppList,HelpdeskOfficeLocation,HelpdeskDepartments,Categories,sub_categories,HelpdeskFulfillerGroups,HelpRequest,Workflow_email_templates
from .service import get_users






def email(key,t_id,emailid,msg):
	#To send email notification
	Email=Workflow_email_templates.objects.values_list('template_body','template_subject').filter(key=key)
	print(t_id)
	message=HelpRequest.objects.values_list('OnBehalfUserEmployeeName','id','created_at','request_type','HelpdeskOffice','department','category','sub_category','priority','description','Files','expected_closure').filter(id=t_id)
	print(message)
	created=datetime.datetime.strptime(str(message[0][2]), '%Y-%m-%d %H:%M:%S.%f+00:00')

	created=created.strftime("%Y-%m-%d %H:%M:%S")
	exp=datetime.datetime.strptime(str(message[0][11]), '%Y-%m-%d %H:%M:%S.%f')
	exp=exp.strftime("%Y-%m-%d %H:%M:%S")
	email_msg=Email[0][0].replace('@@ExpectedClosure',str(exp)).replace('@@message', str(msg)).replace('@@links','<a href="http://127.0.0.1:8000/display/'+str(t_id)+'">Click here</a>' ).replace('@@RequestorName',str(message[0][0])).replace('@@RequestId',str(message[0][1])).replace('@@Created',str(created)).replace('@@TicketType',str(message[0][3])).replace('@@Location',str(message[0][4])).replace('@@DepartmentName',str(message[0][5])).replace('@@CategoryName',str(message[0][6])).replace('@@SubCategoryName',str(message[0][7])).replace('@@Priority',str(message[0][8])).replace('@@Description',str(message[0][9]))
	if(message[0][10]==""):
		files=" "
	else:
		files=settings.MEDIA_URL+message[0][10]
	print(files)
	#print(email_msg)
	try:
		subject=Email[0][1].replace('@@EmployeeName',str(message[0][0]))
	except:
		subject="Ticket 2018-2019/Helpdesk/Request/"+str(t_id)+" -Helpdesk Ticket Updated"
	#print(email_msg)
	to=emailid
	print(to)
	print("&"*100)
	#email=EmailMultiAlternatives(subject,email_msg, 'aditip@nitorinfotech.com', to)
	sender="siddhikhole@gmail.com"
	
	send_html_mail(subject, email_msg, to, sender,files)

	

def autocancel():
	
	threading.Timer(60.0, autocancel).start()
	
	TATHrs=40
	seconds=0
	days=TATHrs/8	
	while TATHrs >= 8:
		seconds=seconds+86400
		TATHrs=TATHrs-8
		
	seconds=seconds+(TATHrs*3600)
	
	a=0
	for i in range(int(days)):
		
		dt1=datetime.datetime.now() + timedelta(i+1)
		if(dt1.strftime("%A") == "Saturday"):
			
			a=a+172800
				
				
	
				
	dt=datetime.datetime.now() + timedelta(seconds=a+seconds)
	
	date=datetime.datetime.strptime(str(datetime.datetime.now()), '%Y-%m-%d %H:%M:%S.%f')
	'''print(date.strftime("%Y-%m-%d %H:%M:%S"))
	print("----"+str(datetime.datetime.now()))
	print(str(dt))'''
	


	###############################################################################################
				#####Auto Cancel#####
	###############################################################################################

	item=HelpRequest.objects.all().filter(WorkflowStatus="Workflow Initiated")

	for i in item:
		#print(datetime.datetime.strptime(str(i.created_at), '%Y-%m-%d %H:%M:%S.%f').date())
		date1 =  str(datetime.datetime.now())
		date1=datetime.datetime.strptime(date1, '%Y-%m-%d %H:%M:%S.%f')
		date2 = str(i.created_at)
		date2=datetime.datetime.strptime(date2, '%Y-%m-%d %H:%M:%S.%f+00:00')
		'''print(date1)
		print(date2)
'''
		
		diff = date1 - date2 
		days = diff.days
	#	print (str(days) + ' day(s)')

		days_to_hours = days * 24
		diff_btw_two_times = (diff.seconds) / 3600
		overall_hours = days_to_hours + diff_btw_two_times
		
		#print (str(overall_hours) + ' hours');

		hours_to_minutes=overall_hours * 60
		diff_btw_two_times = (diff.seconds) / 60
		overall_minutes = hours_to_minutes + diff_btw_two_times
		#print (str(overall_minutes) + ' minutes');
	

		days = np.busday_count( date2.date(), date1.date())
		#print(days) 
		hour=48
		
		
		for d in range(days + 1):
			d1=date2 + timedelta(d)
		#	print(d1.strftime("%A"))

			if(d1.strftime("%A")=="Saturday"):
				hour=hour+48

		#print(d1.strftime("%A"))


		#print("Waiting for: "+str(hour))

		if(overall_hours>hour):
			item2=HelpRequest.objects.get(id=i.id)
			item2.WorkflowStatus="Cancel"
			item2.save()
			item1=WorkflowRequest.objects.get(RequestID_id=i.id,RequestStatus="Pending")
			item1.RequestStatus="Incomplete"
			item1.save()
			form=WorkflowRequest(Process="Cancel",ActedOn=str(datetime.datetime.now()),RequestStatus="Auto Cancelled",RequestID_id=i.id)
			form.save()

			key="HelpdeskTemplate_AssignTask"
			msg="Your attention is requested for following helpdesk ticket-"
			FirstApprover=EmployeeMaster.objects.values_list('email',flat=True).filter(associated_user_account=i.FirstLevelApproverEmployeeName)
			
			
			emailid=HelpRequest.objects.values_list('OnBehalfUserEmployeeId',flat=True).filter(id=i.id)
			Employee=EmployeeMaster.objects.values_list('email',flat=True).filter(empid=emailid[0])
			Employee=[Employee[0],FirstApprover[0]]
			email(key,i.id,Employee,msg)	
		print("_"*50)

	###############################################################################################
				#####Auto Close#####
	###############################################################################################

	item=HelpRequest.objects.all().filter(WorkflowStatus="Completed")
	for i in item:
		#print("#"*40)
		item1=WorkflowRequest.objects.get(Process="Complete",RequestStatus="Completed",RequestID_id=i.id)
		date1 =  str(datetime.datetime.now())
		date1=datetime.datetime.strptime(date1, '%Y-%m-%d %H:%M:%S.%f')
		date2 = str(item1.ActedOn)
		date2=datetime.datetime.strptime(date2, '%Y-%m-%d %H:%M:%S.%f')
		diff = date1 - date2

		days = diff.days
		#print (str(days) + ' day(s)')

		days_to_hours = days * 24
		diff_btw_two_times = (diff.seconds) / 3600
		overall_hours = days_to_hours + diff_btw_two_times
		#print (str(overall_hours) + ' hours');

		hours_to_minutes=overall_hours * 60
		diff_btw_two_times = (diff.seconds) / 60
		overall_minutes = hours_to_minutes + diff_btw_two_times
		#print (str(overall_minutes) + ' minutes');
	

		days = np.busday_count( date2.date(), date1.date())
		#print(days) 
		hour=48
		
		
		for d in range(days + 1):
			d1=date2 + timedelta(d)
	#print(d1.strftime("%A"))

			if(d1.strftime("%A")=="Saturday"):
				hour=hour+48

	#	print(d1.strftime("%A"))


	#	print("Waiting for: "+str(hour))

		if(overall_hours>hour):
			i.WorkflowStatus="Closed"
			i.WorkflowCurrentStatus="Closed"
			i.save()

			item1.Process="Closed"
			item1.save()

			form1=WorkflowRequest(Process="Close",ActedOn=str(datetime.datetime.now()),RequestStatus="Auto Closed",RequestID_id=i.id)
			form1.save()

			key="HelpdeskTemplate_AssignTask"
			msg="Your attention is requested for following helpdesk ticket-"
			
			emailid=HelpRequest.objects.values_list('OnBehalfUserEmployeeId',flat=True).filter(id=i.id)
			Employee=EmployeeMaster.objects.values_list('email',flat=True).filter(empid=emailid[0])
			Employee=[Employee[0]]
			email(key,i.id,Employee,msg)
	#################################################################################
	############Escalation############
	#################################################################################
	item=HelpRequest.objects.all().filter((Q(RequestStatus="1")|Q(RequestStatus="2")),WorkflowStatus="Activated")
	for i in item:
		item1=HelpdeskRequestSLAs.objects.all().filter(HelpdeskCategory=i.category,HelpdeskDepartment=i.department,HelpdeskPriority=i.priority,HelpdeskSubCategory=i.sub_category)
		print(i.WorkflowStatus)
		print(i.id)
		date1 =  str(datetime.datetime.now())
		date1=datetime.datetime.strptime(date1, '%Y-%m-%d %H:%M:%S.%f')
		date2 = str(i.WorkflowModifiedOn)
		date2=datetime.datetime.strptime(date2, '%Y-%m-%d %H:%M:%S.%f+00:00')
		diff = date1 - date2
		
		days = diff.days
	
		#print (str(days) + ' day(s)')

		days_to_hours = days * 24
		diff_btw_two_times = (diff.seconds) / 3600
		overall_hours = days_to_hours + diff_btw_two_times
		#print (str(overall_hours) + ' hours');

		hours_to_minutes=overall_hours * 60
		diff_btw_two_times = (diff.seconds) / 60
		overall_minutes = hours_to_minutes + diff_btw_two_times
		#print (str(overall_minutes) + ' minutes');
		


		days = np.busday_count( date2.date(), date1.date())
		#print(days) 
		for h in item1:
			if(i.RequestStatus=="1"):	
				receiver=h.EM_0_To
				wait=h.EM_0_AfterHrs
				#wait=0.0166667
			elif(i.RequestStatus=="2"):
				wait=h.EM_1_AfterHrs
				#wait=0.0166667
				receiver=h.EM_1_To
				
			else:
				wait=0
			hour=0
			hours=h.TATHrs+wait
			#hours=0.0166667+wait
			while hours >= 8:
				hour=hour+24
				hours=hours-8

		
		
		for d in range(days + 1):
			d1=date2 + timedelta(d)
	#print(d1.strftime("%A"))

			if(d1.strftime("%A")=="Saturday"):
				hour=hour+48

	#	print(d1.strftime("%A"))


		print("Waiting for: "+str(hour))
		print(overall_hours)
		#overall_hours=125
		print(hour-overall_hours)
		if(overall_hours > hour):
			print("HO")
			
			for i1 in item1:
				print(i1.EM_0_To)
				Email=EmployeeMaster.objects.values_list('email',flat=True).filter(empid=receiver)
				print(Email[0])
				Pending=WorkflowRequest.objects.values_list('WorkflowPendingWith',flat=True).filter(RequestStatus="Pending",RequestID_id=i.id)
				print(Pending[0])


				key="HelpdeskTemplate_AssignTask"
				msg="Your attention is requested for following helpdesk ticket pending for "+Pending[0]+"-"
				
				#emailid=HelpRequest.objects.values_list('OnBehalfUserEmployeeId',flat=True).filter(id=i.id)
				#Employee=EmployeeMaster.objects.values_list('email',flat=True).filter(empid=emailid[0])
				Employee=[Email[0]]
				email(key,i.id,Employee,msg)
				if(i.RequestStatus=="1"):
					i.RequestStatus=2
					i.save()
				elif(i.RequestStatus=="2"):
					i.RequestStatus=3
					i.save()
autocancel()

def home(request):
	redirect_uri = request.build_absolute_uri(reverse('HelpDeskApp:gettoken'))
	sign_in_url = get_signin_url(redirect_uri)
	return render(request,"login.html",{'sign_in_url':sign_in_url})

def gettoken(request):
	auth_code = request.GET['code']
	redirect_uri = request.build_absolute_uri(reverse('HelpDeskApp:gettoken'))
	token = get_token_from_code(auth_code, redirect_uri)
	access_token = token['access_token']
	user = get_me(access_token)
	#print(user)
	# Save the token in the session
	request.session['access_token'] = access_token
	user_name=user['mail']
	try:
		print(user_name)
		item=EmployeeMaster.objects.values_list('empid',flat=True).filter(email=user_name)
		request.session['username']=item[0]
	except:
		messages.success("Invalid user...")
		return redirect('home')
	return HttpResponseRedirect('/main')

def fulfiller(request):
	try:
		user=request.session['username']
		user=EmployeeMaster.objects.get(empid=user)
		SLAFullfillerHead=AppList.objects.all().filter(user=user.associated_user_account,roles="HelpdeskFulfillerHead_1")
		FirstApprover=EmployeeMaster.objects.all().filter(reporting_to=user.associated_user_account)
		ApproverHead=AppList.objects.all().filter((Q(roles="HelpdeskAdminApprover1")|Q(roles="HelpdeskFinanceApprover1")|Q(roles="HelpdeskHRApprover1")|Q(roles="HelpdeskITApprover1")),user=user.associated_user_account)
		FulfillerHead=AppList.objects.all().filter((Q(roles="HelpdeskFulfillerHead_HR1")|Q(roles="HelpdeskFulfillerHead_IT1")|Q(roles="HelpdeskFulfillerHead_Admin1")|Q(roles="HelpdeskFulfillerHead_Finance1")),user=user.associated_user_account)
		Fulfiller=HelpdeskFulfillerGroups.objects.all().filter(employee_id=request.session['username'])
		return user,SLAFullfillerHead,FirstApprover,ApproverHead,FulfillerHead,Fulfiller
	except:
		messages.success("Invalid user...")
		return redirect('home')

def main(request):
	

	user,SLAFullfillerHead,FirstApprover,ApproverHead,FulfillerHead,Fulfiller=fulfiller(request)
	return render(request,"index.html",{'Fulfiller':Fulfiller,'user':user,'SLAFulfillerHead':SLAFullfillerHead,'FirstApprover':FirstApprover,'ApproverHead':ApproverHead,'FulfillerHead':FulfillerHead})
	

def pending(request):
	#Default page for Pending tickets
	all_items=HelpRequest.objects.all().filter(OnBehalfUserEmployeeId=request.session['username'],WorkflowStatus="Workflow Initiated")
	all_items = get_users(all_items)
	user,SLAFullfillerHead,FirstApprover,ApproverHead,FulfillerHead,Fulfiller=fulfiller(request)
	return render(request,"pending.html",{'Fulfiller':Fulfiller,'user':user,'SLAFulfillerHead':SLAFullfillerHead,'FirstApprover':FirstApprover,'ApproverHead':ApproverHead,'FulfillerHead':FulfillerHead,'all_items':all_items})
	

def approved(request):
	#Default page for Approved tickets.
	all_items=HelpRequest.objects.all().filter(FirstLevelApproverEmployeeId=request.session['username'],WorkflowStatus="Workflow Initiated")
	all_items = get_users(all_items)
	user,SLAFullfillerHead,FirstApprover,ApproverHead,FulfillerHead,Fulfiller=fulfiller(request)
	return render(request,"approved.html",{'Fulfiller':Fulfiller,'user':user,'SLAFulfillerHead':SLAFullfillerHead,'FirstApprover':FirstApprover,'ApproverHead':ApproverHead,'FulfillerHead':FulfillerHead,'all_items':all_items})



def completed(request):
	#Default page for Completed tickets
	all_items=HelpRequest.objects.all().filter(OnBehalfUserEmployeeId=request.session['username'],WorkflowStatus="Completed")
	all_items = get_users(all_items)
	user,SLAFullfillerHead,FirstApprover,ApproverHead,FulfillerHead,Fulfiller=fulfiller(request)
	return render(request,"complete.html",{'Fulfiller':Fulfiller,'user':user,'SLAFulfillerHead':SLAFullfillerHead,'FirstApprover':FirstApprover,'ApproverHead':ApproverHead,'FulfillerHead':FulfillerHead,'all_items':all_items})


def reopened(request):
	#Default page for Reopend tickets
	all_items=HelpRequest.objects.all().filter(OnBehalfUserEmployeeId=request.session['username'],WorkflowStatus="Reopened")
	all_items = get_users(all_items)
	user,SLAFullfillerHead,FirstApprover,ApproverHead,FulfillerHead,Fulfiller=fulfiller(request)
	return render(request,"reopen.html",{'Fulfiller':Fulfiller,'user':user,'SLAFulfillerHead':SLAFullfillerHead,'FirstApprover':FirstApprover,'ApproverHead':ApproverHead,'FulfillerHead':FulfillerHead,'all_items':all_items})


def raisedQ(request):
	#Default page
	all_items=HelpRequest.objects.all().filter(OnBehalfUserEmployeeId=request.session['username'],WorkflowStatus="Raised Query")
	all_items = get_users(all_items)
	user,SLAFullfillerHead,FirstApprover,ApproverHead,FulfillerHead,Fulfiller=fulfiller(request)
	return render(request,"raisedQ.html",{'Fulfiller':Fulfiller,'user':user,'SLAFulfillerHead':SLAFullfillerHead,'FirstApprover':FirstApprover,'ApproverHead':ApproverHead,'FulfillerHead':FulfillerHead,'all_items':all_items})

def closed(request):
	#Default page
	all_items=HelpRequest.objects.all().filter(OnBehalfUserEmployeeId=request.session['username'],WorkflowStatus="Closed")
	
	all_items = get_users(all_items)
	user,SLAFullfillerHead,FirstApprover,ApproverHead,FulfillerHead,Fulfiller=fulfiller(request)
	return render(request,"closed.html",{'Fulfiller':Fulfiller,'user':user,'SLAFulfillerHead':SLAFullfillerHead,'FirstApprover':FirstApprover,'ApproverHead':ApproverHead,'FulfillerHead':FulfillerHead,'all_items':all_items})

def cancelled(request):
	#Default page
	all_items=HelpRequest.objects.all().filter(OnBehalfUserEmployeeId=request.session['username'],WorkflowStatus="Cancel")	
	all_items = get_users(all_items)
	user,SLAFullfillerHead,FirstApprover,ApproverHead,FulfillerHead,Fulfiller=fulfiller(request)
	return render(request,"cancelled.html",{'Fulfiller':Fulfiller,'user':user,'SLAFulfillerHead':SLAFullfillerHead,'FirstApprover':FirstApprover,'ApproverHead':ApproverHead,'FulfillerHead':FulfillerHead,'all_items':all_items})

def approval(request):
	#Default page
	all_items=HelpRequest.objects.all().filter(FirstLevelApproverEmployeeId=request.session['username'],WorkflowStatus="Workflow Initiated")
	all_items = get_users(all_items)
	user,SLAFullfillerHead,FirstApprover,ApproverHead,FulfillerHead,Fulfiller=fulfiller(request)
	return render(request,"approval.html",{'Fulfiller':Fulfiller,'user':user,'SLAFulfillerHead':SLAFullfillerHead,'FirstApprover':FirstApprover,'ApproverHead':ApproverHead,'FulfillerHead':FulfillerHead,'all_items':all_items})


def rejected(request):
	#Default page
	all_items=HelpRequest.objects.all().filter(OnBehalfUserEmployeeId=request.session['username'],WorkflowStatus="Rejected")
	all_items = get_users(all_items)
	user,SLAFullfillerHead,FirstApprover,ApproverHead,FulfillerHead,Fulfiller=fulfiller(request)
	return render(request,"reject.html",{'Fulfiller':Fulfiller,'user':user,'SLAFulfillerHead':SLAFullfillerHead,'FirstApprover':FirstApprover,'ApproverHead':ApproverHead,'FulfillerHead':FulfillerHead,'all_items':all_items})


def HelpdeskApprover(request):
	#Default page
	name=EmployeeMaster.objects.get(empid=request.session['username'])
	print(name.associated_user_account)
	all_items=" "
	Approver=AppList.objects.all()
	for i in Approver:
		if(i.user==name.associated_user_account and i.roles=="HelpdeskHRApprover1"):
			all_items=WorkflowRequest.objects.all().filter((Q(WorkflowPendingWith="Helpdesk HR Approver")|(Q(WorkflowPendingWith=name.associated_user_account))),RequestStatus="Pending",Process="For Helpdesk Approver")
		elif(i.user==name.associated_user_account and i.roles=="HelpdeskITApprover1"):
			all_items=WorkflowRequest.objects.all().filter(WorkflowPendingWith="Helpdesk IT Approver",RequestStatus="Pending")
		elif(i.user==name.associated_user_account and i.roles=="HelpdeskAdminApprover1"):
			all_items=WorkflowRequest.objects.all().filter(WorkflowPendingWith="Helpdesk Admin Approver",RequestStatus="Pending")
		elif(i.user==name.associated_user_account and i.roles=="HelpdeskFinanceApprover1"):
			all_items=WorkflowRequest.objects.all().filter(WorkflowPendingWith="Helpdesk Finance Approver",RequestStatus="Pending")
	
	tab="HelpdeskApprover"
	total ={}
	user,SLAFullfillerHead,FirstApprover,ApproverHead,FulfillerHead,Fulfiller=fulfiller(request)
	try:
		for i in all_items:
			all_i=HelpRequest.objects.all().filter(id=i.RequestID_id)
			items =get_users(all_i)
			for k,v in items.items():
				total[k] = v

		return render(request,"helpdeskapprover.html",{'Fulfiller':Fulfiller,'user':user,'SLAFulfillerHead':SLAFullfillerHead,'FirstApprover':FirstApprover,'ApproverHead':ApproverHead,'FulfillerHead':FulfillerHead,'all_items':total})
		
	except:
		return render(request,"helpdeskapprover.html",{'Fulfiller':Fulfiller,'user':user,'SLAFulfillerHead':SLAFullfillerHead,'FirstApprover':FirstApprover,'ApproverHead':ApproverHead,'FulfillerHead':FulfillerHead})



def AssignedTickets(request):
	tab="AssignedTickets"
	empName=EmployeeMaster.objects.get(empid=request.session['username'])
	empName=empName.associated_user_account
	all_items=WorkflowRequest.objects.all().filter(ActedByUser=request.session['username'],Process="Complete",WorkflowPendingWith=empName,RequestStatus="Pending")
	print(all_items)
	total ={}
	user,SLAFullfillerHead,FirstApprover,ApproverHead,FulfillerHead,Fulfiller=fulfiller(request)
	try:
		for i in all_items:
			print(i.RequestID_id)
			all_i=HelpRequest.objects.all().filter(id=i.RequestID_id)
			items =get_users(all_i)
			for k,v in items.items():
				total[k] = v

		return render(request,"assigned.html",{'Fulfiller':Fulfiller,'user':user,'SLAFulfillerHead':SLAFullfillerHead,'FirstApprover':FirstApprover,'ApproverHead':ApproverHead,'FulfillerHead':FulfillerHead,'all_items':total,'tab':tab})
		
	except:
		return render(request,"assigned.html",{'tab':tab})
	return render(request,"assigned.html",{'all_items':total,'Fulfiller':Fulfiller,'user':user,'SLAFulfillerHead':SLAFullfillerHead,'FirstApprover':FirstApprover,'ApproverHead':ApproverHead,'FulfillerHead':FulfillerHead,'tab':tab})


def complete(request,ticket_id):

	item1=HelpRequest.objects.get(pk=ticket_id)
	item1.WorkflowStatus="Completed"
	item1.WorkflowCurrentStatus="Completed"
	item1.save()
	item=WorkflowRequest.objects.get(RequestID_id=ticket_id,ActedByUser=request.session['username'],RequestStatus="Pending")
	item.RequestStatus="Completed"
	item.ActedOn=str(datetime.datetime.now())
	item.ActionData=request.GET.get('comments')
	item.WorkflowPendingWith=item1.OnBehalfUserEmployeeName
	item.save()

	key="HelpdeskTemplate_UpdateTicket"
	msg="Your service request is completed of which details are:"
	emailid=HelpRequest.objects.values_list('OnBehalfUserEmployeeId',flat=True).filter(id=ticket_id)
	Employee=EmployeeMaster.objects.values_list('email',flat=True).filter(empid=emailid[0])
	Employee=[Employee[0]]
	email(key,ticket_id,Employee,msg)
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))




def HelpdeskFulfillerHead(request):
	name=EmployeeMaster.objects.get(empid=request.session['username'])
	#print(name.associated_user_account)
	all_items=" "
	Approver=AppList.objects.all()
	for i in Approver:
		if(i.user==name.associated_user_account and i.roles=="HelpdeskFulfillerHead_HR1"):
			all_items=WorkflowRequest.objects.all().filter(WorkflowPendingWith="Helpdesk Fullfiller Head HR",RequestStatus="Pending")
		elif(i.user==name.associated_user_account and i.roles=="HelpdeskFulfillerHead_IT1"):
			all_items=WorkflowRequest.objects.all().filter(WorkflowPendingWith="Helpdesk Fullfiller Head IT",RequestStatus="Pending")
		elif(i.user==name.associated_user_account and i.roles=="HelpdeskFulfillerHead_Admin1"):
			all_items=WorkflowRequest.objects.all().filter(WorkflowPendingWith="Helpdesk Fullfiller Head Admin",RequestStatus="Pending")
		elif(i.user==name.associated_user_account and i.roles=="HelpdeskFulfillerHead_Finance1"):
			all_items=WorkflowRequest.objects.all().filter(WorkflowPendingWith="Helpdesk Fullfiller Head Finance",RequestStatus="Pending")
	
	total ={}
	user,SLAFullfillerHead,FirstApprover,ApproverHead,FulfillerHead,Fulfiller=fulfiller(request)
	try:
		for i in all_items:
			all_i=HelpRequest.objects.all().filter(id=i.RequestID_id)
			items =get_users(all_i)
			for k,v in items.items():
				total[k] = v

		return render(request,"fulfillerhead.html",{'Fulfiller':Fulfiller,'user':user,'SLAFulfillerHead':SLAFullfillerHead,'FirstApprover':FirstApprover,'ApproverHead':ApproverHead,'FulfillerHead':FulfillerHead,'all_items':total})
		
	except:
		return render(request,"fulfillerhead.html",{'Fulfiller':Fulfiller,'user':user,'SLAFulfillerHead':SLAFullfillerHead,'FirstApprover':FirstApprover,'ApproverHead':ApproverHead,'FulfillerHead':FulfillerHead})

	
	
		


def addTicket(request):
	#To add ticket
	if(request.method=="POST"):
		employee_id=request.session['username']
		created_at=datetime.datetime.now()
		description=request.POST.get('Description')
		request_type=request.POST.get('RequestType')
		department=HelpdeskDepartments.objects.values_list('department',flat=True).filter(id=request.POST.get('department'))
		department=department[0]
		category=Categories.objects.values_list('title',flat=True).filter(id=request.POST.get('category'))
		category=category[0]
		sub_category=sub_categories.objects.values_list('title',flat=True).filter(id=request.POST.get('sub_category'))
		sub_category=sub_category[0]
		priority=request.POST.get('priority')
		ticket_for=request.POST.get('yesno')
		onBehalfOf=request.POST.get('onBehalfOf')
		HelpdeskOffice=HelpdeskOfficeLocation.objects.values_list('title',flat=True).filter(id=request.POST.get('officeLocation'))
		HelpdeskOffice=HelpdeskOffice[0]
		DeskLocation=request.POST.get('deskLocation')
		Files=request.FILES.get('documents')
		print("#"*100)
		print(category)
		print(department)
		print(sub_category)
		print(priority)
		print("#"*100)
		try:
			item=HelpdeskRequestSLAs.objects.all().filter(HelpdeskCategory=category,HelpdeskDepartment=department,HelpdeskPriority=priority,HelpdeskSubCategory=sub_category)
			
			for i in item:
				TATHrs=i.TATHrs
			
			seconds=0
			days=TATHrs/8	
			while TATHrs >= 8:
				seconds=seconds+86400
				TATHrs=TATHrs-8
			
			seconds=seconds+(TATHrs*3600)
		
			a=0
			for i in range(int(days)):
			
				dt1=datetime.datetime.now() + timedelta(i+1)
				if(dt1.strftime("%A") == "Saturday"):
				
					a=a+172800
						
			dt=datetime.datetime.now() + timedelta(seconds=a+seconds)
		
		
				
			print(dt)
		except:
			dt=""
		if(ticket_for=="OnBehalf"):

			Employee=EmployeeMaster.objects.values_list('reporting_to','empid','email').filter(associated_user_account=onBehalfOf)
			OnBehalfUserEmployeeId=Employee[0][1]
			OnBehalfUserEmployeeName=onBehalfOf
			Employee1=EmployeeMaster.objects.values_list('associated_user_account','email').filter(empid=employee_id)
			EmployeeName=Employee1[0][0]
		else:
			Employee=EmployeeMaster.objects.values_list('reporting_to','associated_user_account','email').filter(empid=employee_id)
			EmployeeName=Employee[0][1]
			OnBehalfUserEmployeeId=employee_id
			OnBehalfUserEmployeeName=EmployeeName


		FirstLevelApproverEmployeeName=Employee[0][0]
			
		FirstApprover=EmployeeMaster.objects.values_list('empid','email').filter(associated_user_account=FirstLevelApproverEmployeeName)
		FirstLevelApproverEmployeeId=FirstApprover[0][0]
		FirstApproverEmail=FirstApprover[0][1]
		print("#"*40)
		form=HelpRequest(RequestStatus="1",expected_closure=dt,OnBehalfUserEmployeeId=OnBehalfUserEmployeeId,OnBehalfUserEmployeeName=OnBehalfUserEmployeeName,WorkflowStatus="Workflow Initiated",employee_id=employee_id,FirstLevelApproverEmployeeId=FirstLevelApproverEmployeeId,FirstLevelApproverEmployeeName=FirstLevelApproverEmployeeName,EmployeeName=EmployeeName,created_at=created_at,description=description,request_type=request_type,department=department,category=category,sub_category=sub_category,priority=priority,ticket_for=ticket_for,HelpdeskOffice=HelpdeskOffice,DeskLocation=DeskLocation,Files=Files)
		try:
			form.save()

			key='HelpdeskTemplate_AssignTask'
			t_id=form.id
			
			form1=WorkflowRequest(ActedByUser=OnBehalfUserEmployeeId,Process="Raised Ticket",ActedOn=str(datetime.datetime.now()),Action="Raised Ticket",Actor=OnBehalfUserEmployeeName,RequestStatus="Workflow Initiated",WorkflowPendingWith=FirstLevelApproverEmployeeName,RequestID_id=t_id)
			form1.save()
			form1=WorkflowRequest(ActedByUser=FirstLevelApproverEmployeeId,Process="For First Approver",ActedOn=str(datetime.datetime.now()),Actor=FirstLevelApproverEmployeeName,RequestStatus="Pending",WorkflowPendingWith=FirstLevelApproverEmployeeName,RequestID_id=t_id)
			form1.save()
			msg="You have been assigned a service request for approval of which details are:"
			FirstApproverEmail=[FirstApproverEmail]
			email(key,t_id,FirstApproverEmail,msg)
			if(ticket_for=="OnBehalf"):
				key='HelpdeskTemplate_InitiateWorkflow'
				msg="You have raised a service request on behalf of "+onBehalfOf+" for which the details are:"
				to=[Employee1[0][1]]
				
				email(key,t_id,to,msg)

				key='HelpdeskTemplate_InitiateWorkflow'
				msg=EmployeeName+" have raised a service request on behalf of you for which the details are:"
				to=[Employee[0][2]]
				
				email(key,t_id,to,msg)

			else:

				key='HelpdeskTemplate_InitiateWorkflow'
				msg="You have raised a service request of which the details are:"
				to=[Employee[0][2]]
				email(key,t_id,to,msg)
			return HttpResponseRedirect('/main')
		except:
			return HttpResponseRedirect('/main')


def updateTicket(request,ticket_id):
	#To add ticket
	if(request.method=="POST"):
		item=HelpRequest.objects.get(pk=ticket_id)
		item.description=request.POST.get('Description')
		department=HelpdeskDepartments.objects.values_list('department',flat=True).filter(id=request.POST.get('department'))
		item.department=department[0]
		category=Categories.objects.values_list('title',flat=True).filter(id=request.POST.get('category'))
		item.category=category[0]
		sub_category=sub_categories.objects.values_list('title',flat=True).filter(id=request.POST.get('sub_category'))
		item.sub_category=sub_category[0]
		item.priority=request.POST.get('priority')
		HelpdeskOffice=HelpdeskOfficeLocation.objects.values_list('title',flat=True).filter(id=request.POST.get('officeLocation'))
		item.HelpdeskOffice=HelpdeskOffice[0]
		item.DeskLocation=request.POST.get('deskLocation')
		item.Files=request.FILES.get('documents')
		item.save()

		key="HelpdeskTemplate_UpdateTicket"
		msg="Your ticket is updated successfully of which details are:"
		emailid=HelpRequest.objects.values_list('employee_id',flat=True).filter(id=ticket_id)
		Employee=EmployeeMaster.objects.values_list('email',flat=True).filter(empid=emailid[0])
		Employee=[Employee[0]]
		email(key,ticket_id,Employee,msg)
		return HttpResponseRedirect('/main')


def approve(request,ticket_id):
	#To approve ticket 
	print("HI")
	item1=HelpRequest.objects.get(pk=ticket_id)
	item1.WorkflowStatus="Activated"
	item1.WorkflowCurrentStatus="Activated"
	item1.WorkflowModifiedOn=datetime.datetime.now()
	item1.save()
	print(item1.department)
	item=WorkflowRequest.objects.get(RequestID_id=ticket_id,ActedByUser=request.session['username'],RequestStatus="Pending")
	item.RequestStatus="Approved"
	if(item1.department == "HR"):
		item.WorkflowPendingWith="Helpdesk HR Approver"
		roles="HelpdeskHRApprover1"
	elif(item1.department == "IT"):
		item.WorkflowPendingWith="Helpdesk IT Approver"
		roles="HelpdeskITApprover1"
	elif(item1.department == "Admin"):
		item.WorkflowPendingWith="Helpdesk Admin Approver"
		roles="HelpdeskAdminApprover1"
	elif(item1.department == "Finance"):
		item.WorkflowPendingWith="Helpdesk Finance Approver"
		roles="HelpdeskFinanceApprover1"
	item.ActedOn=datetime.datetime.now()
	item.ActionData=request.GET.get('comments')
	#print(ActionData)
	item.save()
	form1=WorkflowRequest(ActedOn=str(datetime.datetime.now()),Actor=item.WorkflowPendingWith,RequestStatus="Pending",WorkflowPendingWith=item.WorkflowPendingWith,Process="For Helpdesk Approver",RequestID_id=ticket_id)
	form1.save()
	

	key="HelpdeskTemplate_UpdateTicket"
	msg="Your service request is approved by "+item1.EmployeeName+" of which details are:"
	emailid=HelpRequest.objects.values_list('OnBehalfUserEmployeeId',flat=True).filter(id=ticket_id)
	Employee=EmployeeMaster.objects.values_list('email',flat=True).filter(empid=emailid[0])
	Employee=[Employee[0]]
	email(key,ticket_id,Employee,msg)


	Employee=[]
	key="HelpdeskTemplate_AssignTask"
	msg="You have been assigned a service request for approval of which details are:"
	user=AppList.objects.all().filter(roles=roles)
	for i in user:
		item=EmployeeMaster.objects.get(associated_user_account=i.user)
		Employee.append(item.email)
	email(key,ticket_id,Employee,msg)
	
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def approve1(request,ticket_id):
	#To approve ticket
	name=EmployeeMaster.objects.get(empid=request.session['username'])
	Approver=AppList.objects.all()
	for i in Approver:
		if(i.user==name.associated_user_account and i.roles=="HelpdeskHRApprover1"):
			item=WorkflowRequest.objects.get((Q(WorkflowPendingWith="Helpdesk HR Approver")|(Q(WorkflowPendingWith=name.associated_user_account))),RequestStatus="Pending",RequestID_id=ticket_id)
			item.WorkflowPendingWith="Helpdesk Fullfiller Head HR"	
			roles="HelpdeskFulfillerHead_HR1"	
		elif(i.user==name.associated_user_account and i.roles=="HelpdeskITApprover1"):
			item=WorkflowRequest.objects.get(RequestID_id=ticket_id,Actor="Helpdesk IT Approver",RequestStatus="Pending")
			item.WorkflowPendingWith="Helpdesk Fullfiller Head IT"	
			roles="HelpdeskFulfillerHead_IT1"
		elif(i.user==name.associated_user_account and i.roles=="HelpdeskAdminApprover1"):
			item=WorkflowRequest.objects.get(RequestID_id=ticket_id,Actor="Helpdesk Admin Approver",RequestStatus="Pending")
			item.WorkflowPendingWith="Helpdesk Fullfiller Head Admin"

			roles="HelpdeskFulfillerHead_Admin1"		
		elif(i.user==name.associated_user_account and i.roles=="HelpdeskFinanceApprover1"):
			item=WorkflowRequest.objects.get(RequestID_id=ticket_id,Actor="Helpdesk Finance Approver",RequestStatus="Pending")
			item.WorkflowPendingWith="Helpdesk Fullfiller Head Finance"	
			roles="HelpdeskFulfillerHead_Finance1"


	item.RequestStatus="Approved"
	item.ActedByUser=request.session['username']
	item.ActedOn=str(datetime.datetime.now())
	Actor=EmployeeMaster.objects.get(empid=request.session['username'])
	item.Actor=Actor.associated_user_account
	item.ActionData=request.GET.get('comments')
	
	item.save()

	form1=WorkflowRequest(ActedOn=str(datetime.datetime.now()),Process="For Helpdesk Fulfiller Head",Actor=item.WorkflowPendingWith,RequestStatus="Pending",WorkflowPendingWith=item.WorkflowPendingWith,RequestID_id=ticket_id)
	print(form1)
	form1.save()
	

	key="HelpdeskTemplate_UpdateTicket"
	msg="Your service request is approved by "+item.Actor+" of which details are:"
	emailid=HelpRequest.objects.values_list('OnBehalfUserEmployeeId',flat=True).filter(id=ticket_id)
	Employee=EmployeeMaster.objects.values_list('email',flat=True).filter(empid=emailid[0])
	Employee=[Employee[0]]
	email(key,ticket_id,Employee,msg)


	Employee=[]
	key="HelpdeskTemplate_AssignTask"
	msg="You have been assigned a service request of which details are:"
	user=AppList.objects.all().filter(roles=roles)
	for i in user:
		item=EmployeeMaster.objects.get(associated_user_account=i.user)
		Employee.append(item.email)
	email(key,ticket_id,Employee,msg)
	
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def reject(request,ticket_id):
	#To reject ticket
	item=HelpRequest.objects.get(pk=ticket_id)
	item.WorkflowStatus="Rejected"
	item.WorkflowCurrentStatus="Rejected"
	item.save()
	item=WorkflowRequest.objects.get(RequestID_id=ticket_id,ActedByUser=request.session['username'])
	item.RequestStatus="Rejected"
	item.ActionData=request.GET.get('comments')
	item.save()
	key="HelpdeskTemplate_UpdateTicket"
	msg="Your service request is rejected of which details are:"
	emailid=HelpRequest.objects.values_list('OnBehalfUserEmployeeId',flat=True).filter(id=ticket_id)
	Employee=EmployeeMaster.objects.values_list('email',flat=True).filter(empid=emailid[0])
	Employee=[Employee[0]]
	email(key,ticket_id,Employee,msg)
	
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def reject1(request,ticket_id):
	#To reject ticket
	item=HelpRequest.objects.get(pk=ticket_id)
	item.WorkflowStatus="Rejected"
	item.WorkflowCurrentStatus="Rejected"
	item.save()
	item=WorkflowRequest.objects.get(RequestID_id=ticket_id,RequestStatus="Pending")
	item.RequestStatus="Rejected"
	item.save()
	key="HelpdeskTemplate_UpdateTicket"
	msg="Your service request is rejected of which details are:"
	emailid=HelpRequest.objects.values_list('OnBehalfUserEmployeeId',flat=True).filter(id=ticket_id)
	Employee=EmployeeMaster.objects.values_list('email',flat=True).filter(empid=emailid[0])
	Employee=[Employee[0]]
	email(key,ticket_id,Employee,msg)
	
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def display(request,ticket_id):
	#To reject ticket
	
	print(ticket_id)
	item=HelpRequest.objects.get(pk=ticket_id)
	emp1=""
	print(item.id)
	try:
		emp=request.session['username']
		empName=EmployeeMaster.objects.get(empid=emp)
		empName=empName.associated_user_account
	except:
		return HttpResponseRedirect('/home')
	Approver=AppList.objects.all()
	for i in Approver:
		if(i.user==empName and i.roles=="HelpdeskHRApprover1"):
			emp1="Helpdesk HR Approver"		
		elif(i.user==empName and i.roles=="HelpdeskITApprover1"):
			emp1="Helpdesk IT Approver"
				
		elif(i.user==empName and i.roles=="HelpdeskAdminApprover1"):
			emp1="Helpdesk Admin Approver"
				
		elif(i.user==empName and i.roles=="HelpdeskFinanceApprover1"):
			emp1="Helpdesk Finance Approver"

	try:
		workflow=WorkflowRequest.objects.get((Q(RequestStatus="Pending")|(Q(RequestStatus="Completed",Process="Complete"))),RequestID_id=ticket_id)
		print(workflow.Process)
		workflow1=WorkflowRequest.objects.all().filter(Action="Raised Query",RequestID_id=ticket_id)
		user,SLAFullfillerHead,FirstApprover,ApproverHead,FulfillerHead,Fulfiller=fulfiller(request)
		return render(request,"display.html",{'Fulfiller':Fulfiller,'user':user,'SLAFulfillerHead':SLAFullfillerHead,'FirstApprover':FirstApprover,'ApproverHead':ApproverHead,'FulfillerHead':FulfillerHead,'item':item,'workflow1':workflow1,'emp':empName,'workflow':workflow,'emp1':emp1})
		
	except:
		return render(request,"display.html",{'item':item,'emp':empName,'emp1':emp1})

def workflow(request,ticket_id):
	#To delete pending ticket
	workflow=WorkflowRequest.objects.all().filter(RequestID_id=ticket_id).order_by('ActedOn')
	print(ticket_id)
	user,SLAFullfillerHead,FirstApprover,ApproverHead,FulfillerHead,Fulfiller=fulfiller(request)
	return render(request,"workflow.html",{'Fulfiller':Fulfiller,'user':user,'SLAFulfillerHead':SLAFullfillerHead,'FirstApprover':FirstApprover,'ApproverHead':ApproverHead,'FulfillerHead':FulfillerHead,'workflow':workflow})

def assign(request,ticket_id):
	name=EmployeeMaster.objects.get(empid=request.session['username'])
	print(name.associated_user_account)
	
	Approver=AppList.objects.all()
	for i in Approver:
		if(i.user==name.associated_user_account and i.roles=="HelpdeskFulfillerHead_HR1"):
			all_items=HelpdeskFulfillerGroups.objects.all().filter(group_name="HR")
		elif(i.user==name.associated_user_account and i.roles=="HelpdeskFulfillerHead_IT1"):
			all_items=HelpdeskFulfillerGroups.objects.all().filter(group_name="IT")
		elif(i.user==name.associated_user_account and i.roles=="HelpdeskFulfillerHead_Admin1"):
			all_items=HelpdeskFulfillerGroups.objects.all().filter(group_name="Admin")
		elif(i.user==name.associated_user_account and i.roles=="HelpdeskFulfillerHead_Finance1"):
			all_items=HelpdeskFulfillerGroups.objects.all().filter(group_name="Finance")
	user,SLAFullfillerHead,FirstApprover,ApproverHead,FulfillerHead,Fulfiller=fulfiller(request)
	return render(request,"assign.html",{'Fulfiller':Fulfiller,'user':user,'SLAFulfillerHead':SLAFullfillerHead,'FirstApprover':FirstApprover,'ApproverHead':ApproverHead,'FulfillerHead':FulfillerHead,'all_items':all_items,'ticket_id':ticket_id})


def assignTicket(request,ticket_id):
	name=EmployeeMaster.objects.get(empid=request.session['username'])

	print(name.associated_user_account)
	Approver=AppList.objects.all()
	for i in Approver:
		
		if(i.user==name.associated_user_account and i.roles=="HelpdeskFulfillerHead_HR1"):
			item=WorkflowRequest.objects.get(RequestID_id=ticket_id,Actor="Helpdesk Fullfiller Head HR",RequestStatus="Pending")
			
		elif(i.user==name.associated_user_account and i.roles=="HelpdeskFulfillerHead_IT1"):
			item=WorkflowRequest.objects.get(RequestID_id=ticket_id,Actor="Helpdesk Fullfiller Head IT",RequestStatus="Pending")
				
		elif(i.user==name.associated_user_account and i.roles=="HelpdeskFulfillerHead_Admin1"):
			item=WorkflowRequest.objects.get(RequestID_id=ticket_id,Actor="Helpdesk Fullfiller Head Admin",RequestStatus="Pending")
			
		elif(i.user==name.associated_user_account and i.roles=="HelpdeskFulfillerHead_Finance1"):
			item=WorkflowRequest.objects.get(RequestID_id=ticket_id,Actor="Helpdesk Fullfiller Head Finance",RequestStatus="Pending")
	item.RequestStatus="Assigned"

	item.ActedByUser=request.session['username']
	item.ActedOn=str(datetime.datetime.now())
	Actor=EmployeeMaster.objects.get(empid=request.session['username'])

	item.ActionData=request.POST.get('comments')
	item.Actor=Actor.associated_user_account
	item.save()
	assignTo=request.POST.get('assignTo')
	assignTo=EmployeeMaster.objects.get(empid=assignTo)
	assignToName=assignTo.associated_user_account

	item1=HelpRequest.objects.get(id=ticket_id)

	form1=WorkflowRequest(ActedByUser=assignTo.empid,Process="Complete",ActedOn=str(datetime.datetime.now()),Actor=assignToName,RequestStatus="Pending",WorkflowPendingWith=assignToName,RequestID_id=ticket_id)
	form1.save()


	##########################################################
	key="HelpdeskTemplate_UpdateTicket"
	msg="Your service request is assigned to "+assignToName+" of which details are:"
	emailid=HelpRequest.objects.values_list('OnBehalfUserEmployeeId',flat=True).filter(id=ticket_id)
	Employee=EmployeeMaster.objects.values_list('email',flat=True).filter(empid=emailid[0])
	Employee=[Employee[0]]
	email(key,ticket_id,Employee,msg)

	key="HelpdeskTemplate_AssignTask"
	msg="You have been assigned a service request for fulfillment of which details are:"
	
	Employee=[assignTo.email]
	email(key,ticket_id,Employee,msg)
	#########################################################
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def update(request,ticket_id):
	#To delete pending ticket
	item=HelpRequest.objects.get(pk=ticket_id)
	officelocation=HelpdeskOfficeLocation.objects.all()
	departments=HelpdeskDepartments.objects.all().filter(request_type="Request")
	category=Categories.objects.all()
	subCategory=sub_categories.objects.all()
	employee=EmployeeMaster.objects.all()
	user,SLAFullfillerHead,FirstApprover,ApproverHead,FulfillerHead,Fulfiller=fulfiller(request)

	
	return render(request,"raiseTicket.html",{'Fulfiller':Fulfiller,'user':user,'SLAFulfillerHead':SLAFullfillerHead,'FirstApprover':FirstApprover,'ApproverHead':ApproverHead,'FulfillerHead':FulfillerHead,'employee':employee,'item':item,'subCategory':subCategory,'officelocation':officelocation,'departments':departments,'category':category})


def log(request):
	return render(request, "login.html",{})

def raiseTicket(request):
	officelocation=HelpdeskOfficeLocation.objects.all()
	departments=HelpdeskDepartments.objects.all().filter(request_type="Request")
	category=Categories.objects.all()
	subCategory=sub_categories.objects.all()
	firstApprover=EmployeeMaster.objects.values_list('reporting_to',flat=True).filter(empid=request.session['username'])
	firstApprover=firstApprover[0]
	employee=EmployeeMaster.objects.all()
	user,SLAFullfillerHead,FirstApprover,ApproverHead,FulfillerHead,Fulfiller=fulfiller(request)
	return render(request, "raiseTicket.html",{'Fulfiller':Fulfiller,'user':user,'SLAFulfillerHead':SLAFullfillerHead,'FirstApprover':FirstApprover,'ApproverHead':ApproverHead,'FulfillerHead':FulfillerHead,'employee':employee,'firstApprover':firstApprover,'subCategory':subCategory,'officelocation':officelocation,'departments':departments,'category':category})

def raiseQuery(request,ticket_id):
	item=HelpRequest.objects.get(id=ticket_id)

	print(item.EmployeeName)
	item.WorkflowStatus="Raised Query"
	name=EmployeeMaster.objects.get(empid=request.session['username'])


	

	item.save()
	try:
		item1=WorkflowRequest.objects.get(RequestID_id=ticket_id,ActedByUser=request.session['username'],RequestStatus="Pending",Process="For First Approver")
	except:
		
		Approver=AppList.objects.all()
		for i in Approver:
			if(i.user==name.associated_user_account and i.roles=="HelpdeskHRApprover1"):
				item1=WorkflowRequest.objects.get((Q(WorkflowPendingWith="Helpdesk HR Approver")|(Q(WorkflowPendingWith=name.associated_user_account))),RequestStatus="Pending",Process="For Helpdesk Approver",RequestID_id=ticket_id)
					
			elif(i.user==name.associated_user_account and i.roles=="HelpdeskITApprover1"):
				item1=WorkflowRequest.objects.get(RequestID_id=ticket_id,Actor="Helpdesk IT Approver",RequestStatus="Pending")
					
			elif(i.user==name.associated_user_account and i.roles=="HelpdeskAdminApprover1"):
				item1=WorkflowRequest.objects.get(RequestID_id=ticket_id,Actor="Helpdesk Admin Approver",RequestStatus="Pending")
						
			elif(i.user==name.associated_user_account and i.roles=="HelpdeskFinanceApprover1"):
				item1=WorkflowRequest.objects.get(RequestID_id=ticket_id,Actor="Helpdesk Finance Approver",RequestStatus="Pending")
	item1.Action="Raised Query"			
	item1.RequestStatus="Raised Query"
	item1.ActedOn=str(datetime.datetime.now())
	item1.ActionData=request.GET.get('comments')
	item1.ActedByUser=name.empid
	item1.Actor=name.associated_user_account
	item1.WorkflowPendingWith=name.associated_user_account
	item1.save()


	form=WorkflowRequest(ActedByUser=item.OnBehalfUserEmployeeId,Process="Answer Query",ActedOn=str(datetime.datetime.now()),Actor=item.OnBehalfUserEmployeeName,RequestStatus="Pending",WorkflowPendingWith=item.OnBehalfUserEmployeeName,RequestID_id=ticket_id)
	form.save()

	key="HelpdeskTemplate_AssignTask"
	msg=name.associated_user_account+" raised a query for ticket of which details are:"
	emailid=HelpRequest.objects.values_list('OnBehalfUserEmployeeId',flat=True).filter(id=ticket_id)
	Employee=EmployeeMaster.objects.values_list('email',flat=True).filter(empid=emailid[0])
	Employee=[Employee[0]]
	email(key,ticket_id,Employee,msg)
	
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))





def cancel(request,ticket_id):
	item=HelpRequest.objects.get(id=ticket_id)
	item.WorkflowStatus="Cancel"
	item.save()
	item1=WorkflowRequest.objects.get(RequestID_id=ticket_id,RequestStatus="Pending")
	item1.RequestStatus="Incomplete"
	item1.save()
	form=WorkflowRequest(ActedByUser=request.session['username'],Process="Cancel",ActedOn=str(datetime.datetime.now()),Actor=item.OnBehalfUserEmployeeName,RequestStatus="Cancelled",RequestID_id=ticket_id)
	form.save()

	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



def ansQuery(request,ticket_id):
	item=HelpRequest.objects.get(id=ticket_id)

	print(item.OnBehalfUserEmployeeName)
			
	item.WorkflowStatus=item.WorkflowCurrentStatus

	print(item.WorkflowStatus)

	item1=WorkflowRequest.objects.get(RequestID_id=ticket_id,ActedByUser=request.session['username'],RequestStatus="Pending")
	item1.RequestStatus="Answered Query"
	item1.ActedOn=str(datetime.datetime.now())
	item1.ActionData=request.GET.get('comments')
	

	item2=WorkflowRequest.objects.get(Action="Raised Query",RequestStatus="Raised Query",RequestID_id=ticket_id)
	item.save()
	item1.save()
	form=WorkflowRequest(ActedByUser=item2.ActedByUser,Process=item2.Process,ActedOn=str(datetime.datetime.now()),Actor=item2.Actor,RequestStatus="Pending",WorkflowPendingWith=item2.Actor,RequestID_id=ticket_id)
	form.save()
	print(item2.Process)
	item2.Action="Raise Query"
	item2.save()


	key="HelpdeskTemplate_AssignTask"
	msg=item.OnBehalfUserEmployeeName+" answered a query for ticket of which details are:"
	emailid=HelpRequest.objects.values_list('OnBehalfUserEmployeeId',flat=True).filter(id=ticket_id)
	Employee=EmployeeMaster.objects.values_list('email',flat=True).filter(empid=item2.ActedByUser)
	Employee=[Employee[0]]
	email(key,ticket_id,Employee,msg)

	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def Reopen(request,ticket_id):
	item=WorkflowRequest.objects.get(RequestID_id=ticket_id,RequestStatus="Completed",Process="Complete")
	item.Process="Reopened"
	item.save()

	item1=HelpRequest.objects.get(id=ticket_id)
	item1.WorkflowStatus="Reopened"
	item1.WorkflowCurrentStatus="Reopened"
	item1.save()

	comments=request.GET.get('comments')

	form1=WorkflowRequest(ActionData=comments,ActedByUser=request.session['username'],Process="Reopen",ActedOn=str(datetime.datetime.now()),Actor=item1.OnBehalfUserEmployeeName,RequestStatus="Reopened",WorkflowPendingWith=item.Actor,RequestID_id=ticket_id)
	form1.save()

	form=WorkflowRequest(ActedByUser=item.ActedByUser,ActedOn=str(datetime.datetime.now()),Actor=item.Actor,Process="Complete",RequestStatus="Pending",WorkflowPendingWith=item.Actor,RequestID_id=ticket_id)
	form.save()

	key="HelpdeskTemplate_AssignTask"
	msg=item1.OnBehalfUserEmployeeName+" reopened ticket of which details are:"
	emailid=HelpRequest.objects.values_list('OnBehalfUserEmployeeId',flat=True).filter(id=ticket_id)
	Employee=EmployeeMaster.objects.values_list('email',flat=True).filter(empid=item.ActedByUser)
	Employee=[Employee[0]]
	email(key,ticket_id,Employee,msg)

	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))	

def Close(request,ticket_id):
	item=HelpRequest.objects.get(id=ticket_id)
	item.WorkflowStatus="Closed"
	item.WorkflowCurrentStatus="Closed"
	item.save()

	item1=WorkflowRequest.objects.get(RequestID_id=ticket_id,RequestStatus="Completed",Process="Complete")
	item1.Process="Closed"
	item1.save()

	comments=request.GET.get('comments')

	form1=WorkflowRequest(ActionData=comments,ActedByUser=request.session['username'],Process="Close",ActedOn=str(datetime.datetime.now()),Actor=item.OnBehalfUserEmployeeName,RequestStatus="Closed",RequestID_id=ticket_id)
	form1.save()

	key="HelpdeskTemplate_AssignTask"
	msg="You closed a service ticket of which details are:"
	emailid=HelpRequest.objects.values_list('OnBehalfUserEmployeeId',flat=True).filter(id=ticket_id)
	Employee=EmployeeMaster.objects.values_list('email',flat=True).filter(empid=emailid[0])
	Employee=[Employee[0]]
	email(key,ticket_id,Employee,msg)
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))	





def logout(request):
	
	user=request.session['username']
	key_variable = request.session.pop('username')
	
	#del request.session['username']
	#messages.success(request, key_variable+" logged out")
	return redirect('home')


def sla(request):
	all_items=HelpdeskRequestSLAs.objects.all().order_by('HelpdeskDepartment','HelpdeskCategory','HelpdeskSubCategory')
	paginator=Paginator(all_items,10)
	page=request.GET.get('page')
	user,SLAFullfillerHead,FirstApprover,ApproverHead,FulfillerHead,Fulfiller=fulfiller(request)
	try:
		contacts=paginator.page(page)
	except:
		contacts=paginator.page(1)
	return render(request,"sla.html",{'Fulfiller':Fulfiller,'user':user,'SLAFulfillerHead':SLAFullfillerHead,'FirstApprover':FirstApprover,'ApproverHead':ApproverHead,'FulfillerHead':FulfillerHead,'all_items':contacts})

def slas(request,ticket_id):
	officelocation=HelpdeskOfficeLocation.objects.all()
	departments=HelpdeskDepartments.objects.all().filter(request_type="Request")
	category=Categories.objects.all()
	subCategory=sub_categories.objects.all()
	employee=EmployeeMaster.objects.all()
	print(ticket_id)
	try:
		ticket_id=HelpdeskRequestSLAs.objects.get(pk=ticket_id)
		return render(request,"edit_sla.html",{'ticket':ticket_id,'employee':employee,'subCategory':subCategory,'officelocation':officelocation,'departments':departments,'category':category})	
	except:
		return render(request,"edit_sla.html",{'employee':employee,'subCategory':subCategory,'officelocation':officelocation,'departments':departments,'category':category})

def edit_sla(request, ticket_id):
	item=HelpdeskRequestSLAs.objects.get(pk=ticket_id)
	item.TATHrs=request.POST.get('TATHrs')
	item.TATMins=request.POST.get('TATMins')
	item.EM_0_AfterHrs=request.POST.get('EM_0_AfterHrs')
	item.EM_1_AfterHrs=request.POST.get('EM_1_AfterHrs')	
	item.EM_0_AfterMin=request.POST.get('EM_0_AfterMin')
	item.EM_1_AfterMin=request.POST.get('EM_1_AfterMin')
	item.EM_0_Name=request.POST.get('EM_0_Name')
	item.EM_1_Name=request.POST.get('EM_1_Name')
	EM_0_To=EmployeeMaster.objects.values_list('empid',flat=True).filter(associated_user_account=request.POST.get('EM_0_Name'))
	
	EM_1_To=EmployeeMaster.objects.values_list('empid',flat=True).filter(associated_user_account=request.POST.get('EM_1_Name'))
	try:
		print(EM_0_To[0],EM_1_To[0])
	except:
		messages.warning(request, 'Invalid employee name.')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	item.EM_1_To=EM_0_To[0]
	item.EM_0_To=EM_1_To[0]
	item.save()

	print("%"*50)
	messages.warning(request, 'Successfully Edited')
	
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def add_sla(request):
	
	req_type=request_type=request.POST.get('type')
	HelpdeskLocation=request.POST.get('location')

	department=HelpdeskDepartments.objects.values_list('department',flat=True).filter(id=request.POST.get('department'))
	print(department)
	HelpdeskDepartment=department[0]
	category=Categories.objects.values_list('title',flat=True).filter(id=request.POST.get('category'))
	HelpdeskCategory=category[0]
	sub_category=sub_categories.objects.values_list('title',flat=True).filter(id=request.POST.get('sub_category'))
	HelpdeskSubCategory=sub_category[0]
	HelpdeskPriority=request.POST.get('priority')
	try:
		HelpdeskRequestSLAs.objects.get(HelpdeskDepartment=HelpdeskDepartment,HelpdeskCategory=HelpdeskCategory,HelpdeskSubCategory=HelpdeskSubCategory,HelpdeskPriority=HelpdeskPriority)
		messages.warning(request, 'THis SLA already exists. You can edit it.')	
	except:	
		print("^"*50)	
		TATHrs=request.POST.get('TATHrs')
		TATMins=request.POST.get('TATMins')
		EM_0_AfterHrs=request.POST.get('EM_0_AfterHrs')
		EM_1_AfterHrs=request.POST.get('EM_1_AfterHrs')	
		EM_0_AfterMin=request.POST.get('EM_0_AfterMin')
		EM_1_AfterMin=request.POST.get('EM_1_AfterMin')
		EM_0_Name=request.POST.get('EM_0_Name')
		EM_1_Name=request.POST.get('EM_1_Name')
		print(HelpdeskDepartment,HelpdeskSubCategory,HelpdeskPriority,TATHrs,TATMins,EM_0_AfterHrs,EM_0_AfterMin,EM_0_Name,EM_1_AfterHrs,EM_0_AfterMin,EM_1_Name)
		EM_0_To=EmployeeMaster.objects.values_list('empid',flat=True).filter(associated_user_account=request.POST.get('EM_0_Name'))
		EM_1_To=EmployeeMaster.objects.values_list('empid',flat=True).filter(associated_user_account=request.POST.get('EM_1_Name'))
		try:
			print(EM_0_To[0],EM_1_To[0])
		except:
			messages.warning(request, 'Invalid employee name.')
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
		print("^"*50)
		EM_1_To=EM_0_To[0]
		EM_0_To=EM_1_To[0]
		form=HelpdeskRequestSLAs(EM_0_AfterHrs=EM_0_AfterHrs,EM_0_AfterMin=EM_0_AfterMin,EM_0_Name=EM_0_Name,EM_0_To=EM_0_To,EM_1_AfterHrs=EM_0_AfterHrs,EM_1_AfterMin=EM_1_AfterMin,EM_1_Name=EM_1_Name,EM_1_To=EM_1_To,HelpdeskCategory=HelpdeskCategory,HelpdeskDepartment=HelpdeskDepartment,HelpdeskLocation=HelpdeskLocation,HelpdeskPriority=HelpdeskPriority,HelpdeskSubCategory=HelpdeskSubCategory,TATHrs=TATHrs,TATMins=TATMins)
		
		form.save()
		print("%"*50)
		messages.warning(request, 'Successfully Added')
		
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))




def delete_sla(request, ticket_id):
	item=HelpdeskRequestSLAs.objects.get(pk=ticket_id)
	item.delete()
	messages.warning(request, 'Successfully Deleted')
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

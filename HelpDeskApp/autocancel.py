import threading
import datetime
from datetime import timedelta
from HelpDesk import settings
from .models import WorkflowRequest,HelpdeskRequestSLAs,EmployeeMaster,AppList,HelpdeskOfficeLocation,HelpdeskDepartments,Categories,sub_categories,HelpdeskFulfillerGroups,HelpRequest,Workflow_email_templates
import numpy as np

class  Autocancel(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        total_hrs = 40
        seconds = 0
        days = total_hrs/8   
        while total_hrs >= 8:
            seconds = seconds + 86400
            total_hrs = total_hrs - 8
          
        seconds = seconds + (total_hrs * 3600)
    
        a = 0
        for i in range(int(days)):
          
            dt1 = datetime.datetime.now() + timedelta(i+1)
            if(dt1.strftime("%A") == "Saturday"):
              
                a = a + 172800
                  
                  
    
                  
        dt = datetime.datetime.now() + timedelta(seconds = a  + seconds)
    
        date = datetime.datetime.strptime(str(datetime.datetime.now()), '%Y-%m-%d %H:%M:%S.%f')
        '''print(date.strftime("%Y-%m-%d %H:%M:%S"))
        print("----"+str(datetime.datetime.now()))
        print(str(dt))'''
    
    
        item = HelpRequest.objects.all().filter(WorkflowStatus = "Workflow Initiated")
        for i in item:
            #print(datetime.datetime.strptime(str(i.created_at), '%Y-%m-%d %H:%M:%S.%f').date())
            date1 =  str(datetime.datetime.now())
            date1 = datetime.datetime.strptime(date1, '%Y-%m-%d %H:%M:%S.%f')
            date2 = str(i.created_at)
            date2 = datetime.datetime.strptime(date2, '%Y-%m-%d %H:%M:%S.%f+00:00')
            '''print(date1)
            print(date2)
''' 
          
            diff = date1 - date2 
            days = diff.days
        #   print (str(days) + ' day(s)')
            days_to_hours = days * 24
            diff_btw_two_times = (diff.seconds) / 3600
            overall_hours = days_to_hours + diff_btw_two_times
          
            #print (str(overall_hours) + ' hours');
            hours_to_minutes = overall_hours * 60
            diff_btw_two_times = (diff.seconds) / 60
            overall_minutes = hours_to_minutes + diff_btw_two_times
            #print (str(overall_minutes) + ' minutes');
    
            days = np.busday_count( date2.date(), date1.date())
            #print(days) 
            hour = 48
            for d in range(days + 1):
                d1 = date2 + timedelta(d)
            #   print(d1.strftime("%A"))
                if(d1.strftime("%A") == "Saturday"):
                    hour = hour + 48
            #print(d1.strftime("%A"))
            #print("Waiting for: "+str(hour))
            if(overall_hours > hour):
                item2 = HelpRequest.objects.get(id = i.id)
                item2.WorkflowStatus = "Cancel"
                item2.WorkflowCurrentStatus = "Cancel"
                item2.save()
                item1 = WorkflowRequest.objects.get(RequestID_id=i.id,RequestStatus="Pending")
                item1.RequestStatus = "Incomplete"
                item1.save()
                form = WorkflowRequest(Process="Cancel",ActedOn=str(datetime.datetime.now()),RequestStatus="Auto Cancelled",RequestID_id=i.id)
                form.save()
                key = "HelpdeskTemplate_AssignTask"
                msg = "Your attention is requested for following helpdesk ticket-"
                FirstApprover = EmployeeMaster.objects.values_list('email',flat=True).filter(associated_user_account=i.FirstLevelApproverEmployeeName)
                emailid = HelpRequest.objects.values_list('OnBehalfUserEmployeeId',flat=True).filter(id=i.id)
                employee = EmployeeMaster.objects.values_list('email',flat=True).filter(empid=emailid[0])
                employee = [employee[0],FirstApprover[0]]
                email(key,i.id,employee,msg)    
            print("_"*50)
        ###############################################################################################
                    #####Auto Close#####
        ###############################################################################################
        item = HelpRequest.objects.all().filter(WorkflowStatus="Completed")
        for i in item:
            #print("#"*40)
            item1 = WorkflowRequest.objects.get(Process="Complete",RequestStatus="Completed",RequestID_id=i.id)
            date1 =  str(datetime.datetime.now())
            date1 = datetime.datetime.strptime(date1, '%Y-%m-%d %H:%M:%S.%f')
            date2 = str(item1.ActedOn)
            date2 = datetime.datetime.strptime(date2, '%Y-%m-%d %H:%M:%S.%f+00:00')
            diff = date1 - date2
            days = diff.days
            #print (str(days) + ' day(s)')
            days_to_hours = days * 24
            diff_btw_two_times = (diff.seconds) / 3600
            overall_hours = days_to_hours + diff_btw_two_times
            #print (str(overall_hours) + ' hours');
            hours_to_minutes = overall_hours * 60
            diff_btw_two_times = (diff.seconds) / 60
            overall_minutes = hours_to_minutes + diff_btw_two_times
            #print (str(overall_minutes) + ' minutes');
    
            days = np.busday_count( date2.date(), date1.date())
            #print(days) 
            hour = 48
          
          
            for d in range(days + 1):
                d1 = date2 + timedelta(d)
        #print(d1.strftime("%A"))
                if(d1.strftime("%A") == "Saturday"):
                    hour = hour+48
        #   print(d1.strftime("%A"))
        #   print("Waiting for: "+str(hour))
            if(overall_hours > hour):
                i.WorkflowStatus = "Closed"
                i.WorkflowCurrentStatus = "Closed"
                i.save()
                item1.Process = "Closed"
                item1.save()
                form1 = WorkflowRequest(Process = "Close" , ActedOn = str(datetime.datetime.now()) , RequestStatus = "Auto Closed",RequestID_id = i.id)
                form1.save()
                key = "HelpdeskTemplate_AssignTask"
                msg = "Your attention is requested for following helpdesk ticket-"
              
                emailid = HelpRequest.objects.values_list('OnBehalfUserEmployeeId',flat = True).filter(id = i.id)
                Employee = EmployeeMaster.objects.values_list('email',flat = True).filter(empid = emailid[0])
                Employee = [Employee[0]]
                email(key,i.id,Employee,msg)
        #################################################################################
        ############Escalation############
        #################################################################################
        item = HelpRequest.objects.all().filter((Q(RequestStatus = "1") | Q(RequestStatus = "2")),WorkflowStatus = "Activated")
        for i in item:
            item1 = HelpdeskRequestSLAs.objects.all().filter(HelpdeskCategory = i.category,HelpdeskDepartment = i.department,HelpdeskPriority = i.priority,HelpdeskSubCategory = i.sub_category)
            print(i.WorkflowStatus)
            print(i.id)
            date1 =  str(datetime.datetime.now())
            date1 = datetime.datetime.strptime(date1, '%Y-%m-%d %H:%M:%S.%f')
            date2 = str(i.WorkflowModifiedOn)
            date2 = datetime.datetime.strptime(date2, '%Y-%m-%d %H:%M:%S.%f+00:00')
            diff = date1 - date2
          
            days = diff.days
    
            #print (str(days) + ' day(s)')
            days_to_hours = days * 24
            diff_btw_two_times = (diff.seconds) / 3600
            overall_hours = days_to_hours + diff_btw_two_times
            #print (str(overall_hours) + ' hours');
            hours_to_minutes = overall_hours * 60
            diff_btw_two_times = (diff.seconds) / 60
            overall_minutes = hours_to_minutes + diff_btw_two_times
            #print (str(overall_minutes) + ' minutes');
          
            days = np.busday_count( date2.date(), date1.date())
            #print(days) 
            for h in item1:
                if(i.RequestStatus == "1"):   
                    receiver = h.EM_0_To
                    wait = h.EM_0_AfterHrs
                    #wait=0.0166667
                elif(i.RequestStatus == "2"):
                    wait = h.EM_1_AfterHrs
                    #wait=0.0166667
                    receiver = h.EM_1_To
                  
                else:
                    wait = 0
                hour = 0
                hours = h.TATHrs + wait
                #hours=0.0166667+wait
                while hours >= 8:
                    hour = hour + 24
                    hours = hours - 8
          
          
            for d in range(days + 1):
                d1 = date2 + timedelta(d)
        #print(d1.strftime("%A"))
                if(d1.strftime("%A") == "Saturday"):
                    hour = hour + 48
        #   print(d1.strftime("%A"))
            print("Waiting for: " + str(hour))
            print(overall_hours)
            #overall_hours=125
            print(hour - overall_hours)
            if(overall_hours > hour):
                print("HO")
              
                for i1 in item1:
                	print("----------------"+str(i.id))
                	print(i1.EM_0_To)
                	Email = EmployeeMaster.objects.values_list('email',flat = True).filter(empid = receiver)
                	print(Email[0])
              	
                	Pending = WorkflowRequest.objects.values_list('WorkflowPendingWith',flat = True).filter(RequestStatus = "Pending",RequestID_id = i.id)
                	print(Pending[0])
                	key = "HelpdeskTemplate_AssignTask"
                	msg = "Your attention is requested for following helpdesk ticket pending for " + Pending[0] + "-"
                	Employee = [Email[0]]
                	email(key,i.id,Employee,msg)
                	if(i.RequestStatus == "1"):
                		i.RequestStatus = 2
                		i.save()
                	elif(i.RequestStatus == "2"):
                		i.RequestStatus = 3
                		i.save()  
def autocancel():
    '''Auomatic close,cancel ticket and escalation matrix'''
    # threading.Timer(1800.0, autocancel).start()
    Autocancel().start()
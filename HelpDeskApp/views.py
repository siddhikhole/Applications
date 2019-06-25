import threading
import matplotlib
import datetime
import calendar
import webbrowser
from datetime import timedelta
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
import os
from django.urls import reverse
from django.contrib import messages
from matplotlib import pyplot as plt
from django.db.models import Q
from django.contrib.auth.models import AnonymousUser
import numpy as np
from HelpDeskApp.authhelper import get_signin_url,get_token_from_code
from HelpDeskApp.outlookservice import get_me
from HelpDeskApp.email import send_html_mail
from HelpDesk import settings
from .models import WorkflowRequest, HelpdeskRequestSLAs, EmployeeMaster, AppList, HelpdeskOfficeLocation, \
    HelpdeskDepartments, Categories, sub_categories, HelpdeskFulfillerGroups, HelpRequest, Workflow_email_templates
from .service import get_users
matplotlib.use('Agg')


def email(key, t_id, email_id, msg):

    """
    Generates email body
    :param key: key in Workflow_email_templates table
    :param t_id: ticket_id to get ticket details
    :param email_id: receivers email id
    :param msg: message in body of email
    :return: call send_html_mail function from email.py
    """

    email_content = Workflow_email_templates.objects.values_list('template_body', 'template_subject').filter(key=key)
    message = HelpRequest.objects.values_list('OnBehalfUserEmployeeName', 'id', 'created_at', 'request_type',
                                              'HelpdeskOffice', 'department', 'category', 'sub_category', 'priority',
                                              'description', 'Files', 'expected_closure').filter(id=t_id)
    created = datetime.datetime.strptime(str(message[0][2]), '%Y-%m-%d %H:%M:%S.%f+00:00')
    created = created.strftime("%Y-%m-%d %H:%M:%S")
    exp = datetime.datetime.strptime(str(message[0][11]), '%Y-%m-%d %H:%M:%S.%f')
    exp = exp.strftime("%Y-%m-%d %H:%M:%S")
    email_msg = email_content[0][0].replace('@@ExpectedClosure', str(exp)).\
        replace('@@message', str(msg)).\
        replace('@@links', '<a href="http://127.0.0.1:8000/display/'+str(t_id)+'">Click here</a>').\
        replace('@@RequestorName', str(message[0][0])).\
        replace('@@RequestId', str(message[0][1])).\
        replace('@@Created', str(created)).\
        replace('@@TicketType', str(message[0][3])).\
        replace('@@Location', str(message[0][4])).\
        replace('@@DepartmentName', str(message[0][5])).\
        replace('@@CategoryName', str(message[0][6])).\
        replace('@@SubCategoryName', str(message[0][7])).\
        replace('@@Priority', str(message[0][8])).\
        replace('@@Description', str(message[0][9]))

    if message[0][10] == "":
        files = " "
    else:
        files = str(settings.MEDIA_URL) + str(message[0][10])
    try:
        subject = email_content[0][1].replace('@@EmployeeName',str(message[0][0]))
    except Exception as e:
        print(e)
        subject = "Ticket 2018-2019/Helpdesk/Request/"+str(t_id)+" -Helpdesk Ticket Updated"
    to = email_id
    sender = "siddhi.khole@nitorinfotech.com"
    send_html_mail(subject, email_msg, to, sender, files)


def auto_cancel():
    """
        sends email for auto cancel, auto close and SLA's escaleted tickets
    """
    # threading.Timer(60.0, auto_cancel).start()
    total_hrs = 40
    seconds = 0
    days = total_hrs / 8
    while total_hrs >= 8:
        seconds = seconds + 86400
        total_hrs = total_hrs - 8
    a = 0
    for i in range(int(days)):
        dt1 = datetime.datetime.now() + timedelta(i + 1)
        if dt1.strftime("%A") == "Saturday":
            a = a + 172800
    item = HelpRequest.objects.all().filter(WorkflowStatus="Workflow Initiated")
    for i in item:
        date1 = str(datetime.datetime.now())
        date1 = datetime.datetime.strptime(date1, '%Y-%m-%d %H:%M:%S.%f')
        date2 = str(i.created_at)
        date2 = datetime.datetime.strptime(date2, '%Y-%m-%d %H:%M:%S.%f+00:00')
        diff = date1 - date2
        days = diff.days
        days_to_hours = days * 24
        diff_btw_two_times = diff.seconds / 3600
        overall_hours = days_to_hours + diff_btw_two_times
        days = np.busday_count(date2.date(), date1.date())
        hour = 48
        for d in range(days + 1):
            d1 = date2 + timedelta(d)
            if d1.strftime("%A") == "Saturday":
                hour = hour + 48
        if overall_hours > hour:
            item2 = HelpRequest.objects.get(id=i.id)
            item2.WorkflowStatus = "Cancel"
            item2.WorkflowCurrentStatus = "AutoCancel"
            item2.save()
            item1 = WorkflowRequest.objects.get(RequestID_id=i.id, RequestStatus="Pending")
            item1.RequestStatus = "Incomplete"
            item1.save()
            form = WorkflowRequest(Process="Cancel", ActedOn=str(datetime.datetime.now()),
                                   RequestStatus="Auto Cancelled", RequestID_id=i.id)
            form.save()
            key = "HelpdeskTemplate_AssignTask"
            msg = "Your attention is requested for following helpdesk ticket-"
            FirstApprover = EmployeeMaster.objects.values_list('email', flat=True).filter(
                associated_user_account=i.FirstLevelApproverEmployeeName)
            emailid = HelpRequest.objects.values_list('OnBehalfUserEmployeeId', flat=True).filter(id=i.id)
            employee = EmployeeMaster.objects.values_list('email', flat=True).filter(empid=emailid[0])
            employee = [employee[0], FirstApprover[0]]
            email(key, i.id, employee, msg)

        """Auto Close"""
        item = HelpRequest.objects.all().filter(WorkflowStatus="Completed")
        for i in item:
            item1 = WorkflowRequest.objects.get(Process="Complete", RequestStatus="Completed", RequestID_id=i.id)
            date1 = str(datetime.datetime.now())
            date1 = datetime.datetime.strptime(date1, '%Y-%m-%d %H:%M:%S.%f')
            date2 = str(item1.ActedOn)
            date2 = datetime.datetime.strptime(date2, '%Y-%m-%d %H:%M:%S.%f+00:00')
            diff = date1 - date2
            days = diff.days
            days_to_hours = days * 24
            diff_btw_two_times = diff.seconds / 3600
            overall_hours = days_to_hours + diff_btw_two_times
            days = np.busday_count(date2.date(), date1.date())
            hour = 48
            for d in range(days + 1):
                d1 = date2 + timedelta(d)
                if d1.strftime("%A") == "Saturday":
                    hour = hour + 48
            if overall_hours > hour:
                i.WorkflowStatus = "Closed"
                i.WorkflowCurrentStatus = "Closed"
                i.save()
                item1.Process = "Closed"
                item1.save()
                form1 = WorkflowRequest(Process="Close", ActedOn=str(datetime.datetime.now()),
                                        RequestStatus="Auto Closed", RequestID_id=i.id)
                form1.save()
                key = "HelpdeskTemplate_AssignTask"
                msg = "Your attention is requested for following helpdesk ticket-"
                emailid = HelpRequest.objects.values_list('OnBehalfUserEmployeeId', flat=True).filter(id=i.id)
                employee = EmployeeMaster.objects.values_list('email', flat=True).filter(empid=emailid[0])
                employee = [employee[0]]
                email(key, i.id, employee, msg)
        """Escalation"""
        item = HelpRequest.objects.all().filter((Q(RequestStatus="1") | Q(RequestStatus="2")),
                                                WorkflowStatus="Activated")
        for i in item:
            item1 = HelpdeskRequestSLAs.objects.all().filter(HelpdeskCategory=i.category,
                                                             HelpdeskDepartment=i.department,
                                                             HelpdeskPriority=i.priority,
                                                             HelpdeskSubCategory=i.sub_category)

            date1 = str(datetime.datetime.now())
            date1 = datetime.datetime.strptime(date1, '%Y-%m-%d %H:%M:%S.%f')
            date2 = str(i.WorkflowModifiedOn)
            date2 = datetime.datetime.strptime(date2, '%Y-%m-%d %H:%M:%S.%f+00:00')
            diff = date1 - date2
            days = diff.days
            days_to_hours = days * 24
            diff_btw_two_times = diff.seconds / 3600
            overall_hours = days_to_hours + diff_btw_two_times
            days = np.busday_count(date2.date(), date1.date())
            for h in item1:
                if i.RequestStatus == "1":
                    receiver = h.EM_0_To
                    wait = h.EM_0_AfterHrs
                elif i.RequestStatus == "2":
                    wait = h.EM_1_AfterHrs
                    # wait=0.0166667
                    receiver = h.EM_1_To
                else:
                    wait = 0
                hour = 0
                hours = h.TATHrs + wait
                while hours >= 8:
                    hour = hour + 24
                    hours = hours - 8
            for d in range(days + 1):
                d1 = date2 + timedelta(d)
                if d1.strftime("%A") == "Saturday":
                    hour = hour + 48
            print("Waiting for: " + str(hour))
            if overall_hours > hour:
                for i1 in item1:
                    Email = EmployeeMaster.objects.values_list('email', flat=True).filter(empid=receiver)
                    Pending = WorkflowRequest.objects.values_list('WorkflowPendingWith', flat=True).filter(
                        RequestStatus="Pending", RequestID_id=i.id)
                    key = "HelpdeskTemplate_AssignTask"
                    msg = "Your attention is requested for following helpdesk ticket pending  "
                    employee = [Email[0]]
                    email(key, i.id, employee, msg)
                    if i.RequestStatus == "1":
                        i.RequestStatus = 2
                        i.save()
                    elif i.RequestStatus == "2":
                        i.RequestStatus = 3
                        i.save()


auto_cancel()


def home(request):
    """
    Default page
    :return : To welcome page/login page
    """
    redirect_uri = request.build_absolute_uri(reverse('HelpDeskApp:gettoken'))
    sign_in_url = get_signin_url(redirect_uri)
    return render(request, "login.html", {'sign_in_url': sign_in_url})


def gettoken(request):
    """
    Authenticate user
    :return: Main page after successful login
    """
    auth_code = request.GET['code']
    redirect_uri = request.build_absolute_uri(reverse('HelpDeskApp:gettoken'))
    token = get_token_from_code(auth_code, redirect_uri)
    access_token = token['access_token']
    user = get_me(access_token)

    """Save the token in the session"""
    request.session['access_token'] = access_token
    user_name = user['mail']
    try:
        print(user_name)
        item = EmployeeMaster.objects.values_list('empid', flat=True).filter(email=user_name)
        request.session['username'] = item[0]
    except Exception as e:
        messages.success("Invalid user")
        print(e)
        return redirect('home')
    return HttpResponseRedirect('/main')


def view_report(request):
    """
    Filters to generates monthly report
    :return: to view_report.html for selecting month and department to generate report
    """
    try:
        user, sla_ful_filler_head, first_approve, approve_head, full_filler_head, ful_filler = fulfiller(request)
    except Exception as e:
        print(e)
        return redirect('home')
    return render(request, "view_Report.html", {'Fulfiller': ful_filler, 'user': user,
                                                'SLAFulfillerHead': sla_ful_filler_head,
                                                'FirstApprover': first_approve, 'ApproverHead': approve_head,
                                                'FulfillerHead': full_filler_head})


def report(request):
    """
    Generates monthly reports using filters
    :return: to report.html to display report's dashboard
    """
    try:
        user, SLAFullfillerHead, FirstApprover, ApproverHead, FulfillerHead, Fulfiller = fulfiller(request)
    except Exception as e:
        print(e)
        return redirect('home')
    if request.method == "POST":
        if request.POST.get('department') == "All":
            Pending = HelpRequest.objects.filter(WorkflowStatus="Workflow Initiated")
            Activated = HelpRequest.objects.filter(WorkflowStatus="Activated")
            completed = HelpRequest.objects.filter((Q(WorkflowStatus="Completed") | (Q(WorkflowStatus="Closed"))),
                                                   RequestStatus="1")
            late_completed = HelpRequest.objects.filter(((Q(RequestStatus="2")) | (Q(RequestStatus="3"))))
            cancelled = HelpRequest.objects.filter(WorkflowStatus="Cancel", WorkflowCurrentStatus="Cancel")
            auto_cancel = HelpRequest.objects.filter(WorkflowStatus="Cancel", WorkflowCurrentStatus="AutoCancel")
            title = plt.title(f"Overall Report ({calendar.month_name[int(request.POST.get('month'))]})")
        else:
            Pending = HelpRequest.objects.filter(WorkflowStatus="Workflow Initiated",
                                                 department=request.POST.get('department'))
            Activated = HelpRequest.objects.filter(WorkflowStatus="Activated",
                                                   department=request.POST.get('department'))
            completed = HelpRequest.objects.filter((Q(WorkflowStatus="Completed") | (Q(WorkflowStatus="Closed"))),
                                                   RequestStatus="1",department=request.POST.get('department'))
            late_completed = HelpRequest.objects.filter(((Q(RequestStatus="2")) | (Q(RequestStatus="3"))),
                                                        department=request.POST.get('department'))
            cancelled = HelpRequest.objects.filter(WorkflowStatus="Cancel", WorkflowCurrentStatus="Cancel",
                                                   department=request.POST.get('department'))
            auto_cancel = HelpRequest.objects.filter(WorkflowStatus="Cancel", WorkflowCurrentStatus="AutoCancel",
                                                     department=request.POST.get('department'))
            title = plt.title(f"Report for {request.POST.get('department')} Department "
                              f"({calendar.month_name[int(request.POST.get('month'))]})")

        """PIE"""
        print(late_completed.count())
        late_count = complete_count = activated_count = pending_count = cancel_count=autocancel_count = 0
        for i in late_completed:
            date_time_obj = datetime.datetime.strptime(i.expected_closure, '%Y-%m-%d %H:%M:%S.%f')
            if str(date_time_obj.month) == request.POST.get('month'):
                late_count += 1
        for i in Pending:
            date_time_obj = datetime.datetime.strptime(i.expected_closure, '%Y-%m-%d %H:%M:%S.%f')
            if str(date_time_obj.month) == request.POST.get('month'):
                pending_count += 1
        for i in Activated:
            date_time_obj = datetime.datetime.strptime(i.expected_closure, '%Y-%m-%d %H:%M:%S.%f')
            if str(date_time_obj.month) == request.POST.get('month'):
                activated_count += 1
        for i in completed:
            date_time_obj = datetime.datetime.strptime(i.expected_closure, '%Y-%m-%d %H:%M:%S.%f')
            if str(date_time_obj.month) == request.POST.get('month'):
                complete_count += 1
        for i in cancelled:
            date_time_obj = datetime.datetime.strptime(i.expected_closure, '%Y-%m-%d %H:%M:%S.%f')
            if str(date_time_obj.month) == request.POST.get('month'):
                cancel_count += 1
        for i in auto_cancel:
            date_time_obj = datetime.datetime.strptime(i.expected_closure, '%Y-%m-%d %H:%M:%S.%f')
            if str(date_time_obj.month) == request.POST.get('month'):
                autocancel_count += 1
        total = [complete_count, late_count, activated_count, pending_count, cancel_count, autocancel_count]
        if sum(total) == 0:
            return render(request, "report.html", {'Fulfiller': Fulfiller, 'user': user,
                                                   'SLAFulfillerHead': SLAFullfillerHead,
                                                   'FirstApprover': FirstApprover, 'ApproverHead': ApproverHead,
                                                   'FulfillerHead': FulfillerHead})
        else:
            labels = ["Completed", "Escalated", "Activated", "Pending", "Cancelled", "Auto-Cancelled"]
            title.set_ha("left")
            plt.gca().axis("equal")
            explode = (0.05, 0.05, 0.05, 0.05, 0.05, 0.05)
            plt.pie(total, startangle=0, pctdistance=0.85, autopct='%1.1f%%', explode=explode)
            centre_circle = plt.Circle((0,0),0.70,fc='white')
            fig = plt.gcf()

            fig.gca().add_artist(centre_circle)

            res_list = []
            for i in range(0, len(total)):
                res_list.append(labels[i] + " ( "+str(total[i]) + " )")
            plt.legend(res_list, bbox_to_anchor=(1,0.5), loc="center right", fontsize=10,
                       bbox_transform=plt.gcf().transFigure)
            plt.subplots_adjust(left=0.07, bottom=0.1, right=0.55)
            plt.savefig("media/report/pie.png")
            plt.close()
            """Pie chart(Achieved vs. Violated Tickets"""
            labels = ["Achived\nTickets", "Violated\nTickets"]
            total = [sum(total)-late_count, late_count]
            plt.gca().axis("equal")
            explode = (0.0, 0.0)
            plt.pie(total, labels=labels, startangle=90, pctdistance=0.85, autopct='%1.1f%%', explode=explode)
            title = plt.title(f"Achived vs. Violated Tickets ({calendar.month_name[int(request.POST.get('month'))]})")
            centre_circle = plt.Circle((0,0),0.80,fc='white')
            fig = plt.gcf()
            title.set_ha("center")
            fig.gca().add_artist(centre_circle)
            res_list = []
            for i in range(0, len(total)):
                res_list.append(labels[i] + " ( "+str(total[i]) + " )")
            plt.subplots_adjust(left=0.06, bottom=0.1, right=0.55)
            plt.savefig("media/report/pie2.png")
            plt.close()
            """Bar Diagram"""
            num_days = calendar.monthrange(2019, int(request.POST.get('month')))[1]
            y = []
            for day in range(1, num_days+1):
                cnt = 0
                for i in late_completed:
                    date_time_obj = datetime.datetime.strptime(i.expected_closure, '%Y-%m-%d %H:%M:%S.%f')
                    date_time_obj = date_time_obj.strftime("%Y-%m-%d")
                    date_time_obj1 = datetime.datetime(2019, int(request.POST.get('month')), day)
                    date_time_obj1 = date_time_obj1.strftime("%Y-%m-%d")
                    if date_time_obj1 == date_time_obj:
                        cnt += 1
                y.append(cnt)
            days = [datetime.date(2019, int(request.POST.get('month')), day) for day in range(1, num_days+1)]
            x = days
            a = []
            for i in days:
                print(i.strftime("%d-%b"))
                a.append(i.strftime("%d %b"))
            plt.figure(figsize=(14, 5))
            plt.bar(a, y, width=0.5, label='SLAs violated tickets\n\nTotal tickets '+str(sum(y)))
            plt.xticks(a, rotation=320, ha='left')
            plt.xlabel('Ticket Count')
            plt.ylabel('Ticket Count')
            plt.title('SLAs violated tickets', fontsize=20)
            plt.legend()
            plt.savefig("media/report/abcde.png")
            plt.close()
            files = "report/abcde.png"
            filess = "report/pie.png"
            files3 = "report/pie2.png"
            return render(request, "report.html", {'files3': files3, 'media_url': settings.MEDIA_URL, 'files': files,
                                                   'filess': filess, 'Fulfiller': Fulfiller, 'user': user,
                                                   'SLAFulfillerHead': SLAFullfillerHead,
                                                   'FirstApprover': FirstApprover, 'ApproverHead': ApproverHead,
                                                   'FulfillerHead': FulfillerHead})
    else:
        return render(request, "view_Report.html", {'Fulfiller': Fulfiller, 'user': user,
                                                    'SLAFulfillerHead':SLAFullfillerHead,
                                                    'FirstApprover': FirstApprover, 'ApproverHead': ApproverHead,
                                                    'FulfillerHead': FulfillerHead})


def fulfiller(request):
    """
    Check roles  of particular user
    :return: user, SLAFullfillerHead, FirstApprover, ApproverHead, FulfillerHead, Fulfiller for adding options
     in sidebar on every page
     """
    try:
        user = request.session['username']
        user = EmployeeMaster.objects.get(empid=user)
    except Exception as e:
        print(e)
        return redirect('home')

    SLAFullfillerHead = AppList.objects.all().filter(user=user.associated_user_account,
                                                     roles="HelpdeskFulfillerHead_1")
    FirstApprover = EmployeeMaster.objects.all().filter(reporting_to=user.associated_user_account)
    ApproverHead = AppList.objects.all().filter((Q(roles="HelpdeskAdminApprover1") | Q(roles="HelpdeskFinanceApprover1")
                                                 | Q(roles="HelpdeskHRApprover1") | Q(roles="HelpdeskITApprover1")),
                                                user=user.associated_user_account)
    FulfillerHead = AppList.objects.all().filter((Q(roles="HelpdeskFulfillerHead_HR1") |
                                                  Q(roles="HelpdeskFulfillerHead_IT1") |
                                                  Q(roles="HelpdeskFulfillerHead_Admin1") |
                                                  Q(roles="HelpdeskFulfillerHead_Finance1")),
                                                 user=user.associated_user_account)
    Fulfiller = HelpdeskFulfillerGroups.objects.all().filter(employee_id=request.session['username'])
    return user, SLAFullfillerHead, FirstApprover, ApproverHead, FulfillerHead, Fulfiller


def main(request):
    """
    Main page after login
    :return: to default page after successfull login
    """
    try:
        user, SLAFullfillerHead, FirstApprover, ApproverHead, FulfillerHead, Fulfiller = fulfiller(request)
    except Exception as e:
        print(e)
        return redirect('home')
    return render(request, "index.html", {'Fulfiller': Fulfiller, 'user': user, 'SLAFulfillerHead': SLAFullfillerHead,
                                          'FirstApprover': FirstApprover, 'ApproverHead': ApproverHead,
                                          'FulfillerHead': FulfillerHead})


def pending(request):
    """
    Display your pending tickets
    :return: to pending.html to display all Pending tickets raised by particular Employee
    """
    try:
        user, SLAFullfillerHead, FirstApprover, ApproverHead, FulfillerHead, Fulfiller = fulfiller(request)
    except Exception as e:
        print(e)
        return redirect('home')
    all_items = HelpRequest.objects.all().filter(OnBehalfUserEmployeeId=request.session['username'],
                                                 WorkflowStatus="Workflow Initiated")
    all_items = get_users(all_items)
    return render(request, "pending.html", {'Fulfiller': Fulfiller, 'user': user, 'SLAFulfillerHead': SLAFullfillerHead,
                                            'FirstApprover': FirstApprover, 'ApproverHead': ApproverHead,
                                            'FulfillerHead': FulfillerHead, 'all_items': all_items})


def approved(request):
    """
    Display your activated tickets
    :return: to approved.html to Display active tickets approved by first approver/manager
    """
    try:
        user, SLAFullfillerHead, FirstApprover, ApproverHead, FulfillerHead, Fulfiller = fulfiller(request)
    except Exception as e:
        print(e)
        return redirect('home')
    all_items = HelpRequest.objects.all().filter(FirstLevelApproverEmployeeId=request.session['username'],
                                                 WorkflowStatus="Activated")
    all_items = get_users(all_items)
    return render(request, "approved.html", {'Fulfiller': Fulfiller, 'user': user,
                                             'SLAFulfillerHead': SLAFullfillerHead, 'FirstApprover': FirstApprover,
                                             'ApproverHead': ApproverHead, 'FulfillerHead': FulfillerHead,
                                             'all_items': all_items})


def completed(request):
    """
    Display your completed tickets
    :return: to completed.html to Display active completed tickets(only for 48 working hours)
    """
    try:
        user, SLAFullfillerHead, FirstApprover, ApproverHead, FulfillerHead, Fulfiller = fulfiller(request)
    except Exception as e:
        print(e)
        return redirect('home')
    all_items = HelpRequest.objects.all().filter(OnBehalfUserEmployeeId=request.session['username'],
                                                 WorkflowStatus="Completed")
    all_items = get_users(all_items)
    return render(request, "complete.html", {'Fulfiller': Fulfiller, 'user': user,
                                             'SLAFulfillerHead': SLAFullfillerHead, 'FirstApprover': FirstApprover,
                                             'ApproverHead': ApproverHead, 'FulfillerHead': FulfillerHead,
                                             'all_items': all_items})


def reopened(request):
    """
    Display tickets that you have reopened
    :return: to reopened.html to Display reopened tickets after completion
    """

    try:
        user, SLAFullfillerHead, FirstApprover, ApproverHead, FulfillerHead, Fulfiller = fulfiller(request)
    except Exception as e:
        print(e)
        return redirect('home')
    all_items = HelpRequest.objects.all().filter(OnBehalfUserEmployeeId=request.session['username'],
                                                 WorkflowStatus="Reopened")
    all_items = get_users(all_items)
    return render(request, "reopen.html", {'Fulfiller': Fulfiller, 'user': user, 'SLAFulfillerHead': SLAFullfillerHead,
                                           'FirstApprover': FirstApprover, 'ApproverHead': ApproverHead,
                                           'FulfillerHead': FulfillerHead, 'all_items': all_items})


def raised_query(request):
    """
    Display tickets which needs more description
    :return: to raisedQ.html to Display active tickets for which first_approver/manager or approver_head raised a query
    """

    try:
        user, SLAFullfillerHead, FirstApprover, ApproverHead, FulfillerHead, Fulfiller = fulfiller(request)
    except Exception as e:
        print(e)
        return redirect('home')
    all_items = HelpRequest.objects.all().filter(OnBehalfUserEmployeeId=request.session['username'],
                                                 WorkflowStatus="Raised Query")
    all_items = get_users(all_items)
    return render(request, "raisedQ.html", {'Fulfiller': Fulfiller, 'user': user, 'SLAFulfillerHead': SLAFullfillerHead,
                                            'FirstApprover': FirstApprover, 'ApproverHead': ApproverHead,
                                            'FulfillerHead': FulfillerHead, 'all_items': all_items})


def closed(request):
    """
    Display your closed tickets
    :return: to closed.html to Display closed tickets after completion manually or automatically
    """

    try:
        user, SLAFullfillerHead, FirstApprover, ApproverHead, FulfillerHead, Fulfiller = fulfiller(request)
    except Exception as e:
        print(e)
        return redirect('home')
    all_items = HelpRequest.objects.all().filter(OnBehalfUserEmployeeId=request.session['username'],
                                                 WorkflowStatus="Closed")
    all_items = get_users(all_items)
    return render(request, "closed.html", {'Fulfiller': Fulfiller, 'user': user, 'SLAFulfillerHead': SLAFullfillerHead,
                                           'FirstApprover': FirstApprover, 'ApproverHead': ApproverHead,
                                           'FulfillerHead': FulfillerHead, 'all_items':all_items})


def cancelled(request):
    """
    Display your manually or automatically cancelled tickets
    :return: to cancelled.html to Display cancelled tickets manually or automatically
    """

    try:
        user, SLAFullfillerHead, FirstApprover, ApproverHead, FulfillerHead, Fulfiller = fulfiller(request)
    except Exception as e:
        print(e)
        return redirect('home')
    all_items = HelpRequest.objects.all().filter(OnBehalfUserEmployeeId=request.session['username'],
                                                 WorkflowStatus="Cancel")
    all_items = get_users(all_items)
    return render(request, "cancelled.html", {'Fulfiller': Fulfiller, 'user': user,
                                              'SLAFulfillerHead': SLAFullfillerHead, 'FirstApprover': FirstApprover,
                                              'ApproverHead': ApproverHead, 'FulfillerHead': FulfillerHead,
                                              'all_items': all_items})


def approval(request):
    """
    Display tickets pending for your approval if you are a first approver
    :return: to approval.html to Display tickets waiting for your(first approver's/ manager's) approval
        (only for 48 working hours)
    """
    try:
        user, SLAFullfillerHead, FirstApprover, ApproverHead, FulfillerHead, Fulfiller = fulfiller(request)
    except Exception as e:
        print(e)
        return redirect('home')
    all_items = HelpRequest.objects.all().filter(FirstLevelApproverEmployeeId=request.session['username'],
                                                 WorkflowStatus="Workflow Initiated")
    all_items = get_users(all_items)
    if FirstApprover:
        return render(request, "approval.html", {'Fulfiller': Fulfiller, 'user': user,
                                                 'SLAFulfillerHead': SLAFullfillerHead, 'FirstApprover': FirstApprover,
                                                 'ApproverHead': ApproverHead, 'FulfillerHead': FulfillerHead,
                                                 'all_items': all_items})
    else:
        return HttpResponseRedirect('/main')


def rejected(request):
    """
    Display your tickets rejected by firsts approver or Helpdesk Approver
        :return: to rejected.html to Display tickets rejected by first approver's/ managers approval
    """
    try:
        user, SLAFullfillerHead, FirstApprover, ApproverHead, FulfillerHead, Fulfiller = fulfiller(request)
    except Exception as e:
        print(e)
        return redirect('home')
    all_items = HelpRequest.objects.all().filter(OnBehalfUserEmployeeId=request.session['username'],
                                                 WorkflowStatus="Rejected")
    all_items = get_users(all_items)
    return render(request, "reject.html", {'Fulfiller': Fulfiller, 'user': user, 'SLAFulfillerHead': SLAFullfillerHead,
                                           'FirstApprover': FirstApprover, 'ApproverHead':ApproverHead,
                                           'FulfillerHead': FulfillerHead, 'all_items': all_items})


def help_desk_approve(request):
    """
    Display tickets pending for your approval if you are a Helpdesk approver
    :return: to helpdeskapprover.html to Display tickets waiting for your(Helpdesk approver head's) approval
    """
    try:
        user, SLAFullfillerHead, FirstApprover, ApproverHead, FulfillerHead, Fulfiller = fulfiller(request)
    except Exception as e:
        print(e)
        return redirect('home')
    name = EmployeeMaster.objects.get(empid=request.session['username'])
    print(name.associated_user_account)
    all_items = " "
    Approver = AppList.objects.all()
    """Checks if you are a Helpdesk approver and for which department """
    for i in Approver:
        if i.user == name.associated_user_account and i.roles == "HelpdeskHRApprover1":
            all_items = WorkflowRequest.objects.all().filter((Q(WorkflowPendingWith="Helpdesk HR Approver") |
                                                              (Q(WorkflowPendingWith=name.associated_user_account))),
                                                             RequestStatus="Pending", Process="For Helpdesk Approver")
        elif i.user == name.associated_user_account and i.roles == "HelpdeskITApprover1":
            all_items = WorkflowRequest.objects.all().filter(WorkflowPendingWith="Helpdesk IT Approver",
                                                             RequestStatus="Pending")
        elif i.user == name.associated_user_account and i.roles == "HelpdeskAdminApprover1":
            all_items = WorkflowRequest.objects.all().filter(WorkflowPendingWith="Helpdesk Admin Approver",
                                                             RequestStatus="Pending")
        elif i.user == name.associated_user_account and i.roles == "HelpdeskFinanceApprover1":
            all_items = WorkflowRequest.objects.all().filter(WorkflowPendingWith="Helpdesk Finance Approver",
                                                             RequestStatus="Pending")
    total = {}
    try:
        for i in all_items:
            all_i = HelpRequest.objects.all().filter(id=i.RequestID_id)
            items = get_users(all_i)
            for k, v in items.items():
                total[k] = v
        if ApproverHead:
            return render(request, "helpdeskapprover.html", {'Fulfiller': Fulfiller, 'user': user,
                                                             'SLAFulfillerHead': SLAFullfillerHead,
                                                             'FirstApprover': FirstApprover,
                                                             'ApproverHead': ApproverHead,
                                                             'FulfillerHead': FulfillerHead, 'all_items': total})
        else:
            return HttpResponseRedirect('/main')
    except Exception as e:
        print(e)
        if ApproverHead:
            return render(request, "helpdeskapprover.html", {'Fulfiller': Fulfiller, 'user': user,
                                                             'SLAFulfillerHead': SLAFullfillerHead,
                                                             'FirstApprover': FirstApprover,
                                                             'ApproverHead': ApproverHead,
                                                             'FulfillerHead': FulfillerHead})
        else:
            return HttpResponseRedirect('/main')


def assigned_tickets(request):
    """
    Display tickets assigned to you
    :return: To assigned.html to display tickets assigned to you(Fulfiller)
    """
    try:
        user, SLAFullfillerHead, FirstApprover, ApproverHead,FulfillerHead,Fulfiller = fulfiller(request)
    except Exception as e:
        print(e)
        return redirect('home')
    emp_name = EmployeeMaster.objects.get(empid=request.session['username'])
    emp_name = emp_name.associated_user_account
    all_items = WorkflowRequest.objects.all().filter(ActedByUser=request.session['username'], Process="Complete",
                                                     WorkflowPendingWith=emp_name, RequestStatus="Pending")
    total = {}
    try:
        for i in all_items:
            all_i = HelpRequest.objects.all().filter(id=i.RequestID_id)
            items = get_users(all_i)
            for k,v in items.items():
                total[k] = v
        if Fulfiller:
            return render(request, "assigned.html", {'Fulfiller': Fulfiller, 'user': user,
                                                     'SLAFulfillerHead': SLAFullfillerHead,
                                                     'FirstApprover': FirstApprover, 'ApproverHead': ApproverHead,
                                                     'FulfillerHead': FulfillerHead, 'all_items': total})
        else:
            return HttpResponseRedirect('/main')
    except Exception as e:
        print(e)
        if Fulfiller:
            return render(request, "assigned.html", {'all_items': total, 'Fulfiller': Fulfiller, 'user': user,
                                                     'SLAFulfillerHead': SLAFullfillerHead,
                                                     'FirstApprover': FirstApprover, 'ApproverHead': ApproverHead,
                                                     'FulfillerHead': FulfillerHead})
        else:
            return HttpResponseRedirect('/main')


def complete(request, ticket_id):
    """
    Completes ticket after fulfillment
    :param request: to fulfill ticket
    :param ticket_id: id of ticket which is to be completed
    :return: to prvious page
    """
    item1 = HelpRequest.objects.get(pk=ticket_id)
    item1.WorkflowStatus = "Completed"
    item1.WorkflowCurrentStatus = "Completed"
    item1.save()
    item = WorkflowRequest.objects.get(RequestID_id=ticket_id, ActedByUser=request.session['username'],
                                       RequestStatus="Pending")
    item.RequestStatus = "Completed"
    item.ActedOn = str(datetime.datetime.now())
    item.ActionData = request.GET.get('comments')
    item.WorkflowPendingWith = item1.OnBehalfUserEmployeeName
    item.save()
    if item1.InActive == "on":
        key = "HelpdeskTemplate_UpdateTicket"
        msg = "Your service request is completed of which details are:"
        email_id = HelpRequest.objects.values_list('OnBehalfUserEmployeeId', flat=True).filter(id=ticket_id)
        employee = EmployeeMaster.objects.values_list('email', flat=True).filter(empid=email_id[0])
        employee = [employee[0]]
        email(key, ticket_id, employee, msg)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def help_desk_ful_filler_head(request):
    """
    Returns data of fulfiller head
    :param request: to get data of fulfiller head
    :return: data of tickets pending for your(Fulfiller HEad's approval)
    """
    try:
        user, SLAFullfillerHead, FirstApprover, ApproverHead, FulfillerHead, Fulfiller = fulfiller(request)
    except Exception as e:
        print(e)
        return redirect('home')
    name = EmployeeMaster.objects.get(empid=request.session['username'])
    all_items = " "
    approver = AppList.objects.all()
    for i in approver:
        if i.user == name.associated_user_account and i.roles == "HelpdeskFulfillerHead_HR1":
            all_items = WorkflowRequest.objects.all().filter(WorkflowPendingWith="Helpdesk Fullfiller Head HR",
                                                             RequestStatus="Pending")
        elif i.user == name.associated_user_account and i.roles == "HelpdeskFulfillerHead_IT1":
            all_items = WorkflowRequest.objects.all().filter(WorkflowPendingWith="Helpdesk Fullfiller Head IT",
                                                             RequestStatus="Pending")
        elif i.user == name.associated_user_account and i.roles == "HelpdeskFulfillerHead_Admin1":
            all_items = WorkflowRequest.objects.all().filter(WorkflowPendingWith="Helpdesk Fullfiller Head Admin",
                                                             RequestStatus="Pending")
        elif i.user == name.associated_user_account and i.roles == "HelpdeskFulfillerHead_Finance1":
            all_items = WorkflowRequest.objects.all().filter(WorkflowPendingWith="Helpdesk Fullfiller Head Finance",
                                                             RequestStatus="Pending")

    total = {}
    try:
        for i in all_items:
            all_i = HelpRequest.objects.all().filter(id=i.RequestID_id)
            items = get_users(all_i)
            for k, v in items.items():
                total[k] = v

        return render(request, "fulfillerhead.html", {'Fulfiller': Fulfiller, 'user': user,
                                                      'SLAFulfillerHead':SLAFullfillerHead,
                                                      'FirstApprover': FirstApprover, 'ApproverHead': ApproverHead,
                                                      'FulfillerHead': FulfillerHead, 'all_items': total})

    except Exception as e:
        print(e)
        return render(request, "fulfillerhead.html", {'Fulfiller': Fulfiller, 'user': user,
                                                      'SLAFulfillerHead': SLAFullfillerHead,
                                                      'FirstApprover': FirstApprover, 'ApproverHead': ApproverHead,
                                                      'FulfillerHead': FulfillerHead})


def add_ticket(request):
    """
    To add ticket
    :param request: to raise a ticket
    :return: to previous page after raising ticket
    """
    if request.method == "POST":
        employee_id = request.session['username']
        created_at = datetime.datetime.now()
        description = request.POST.get('Description')
        request_type = request.POST.get('RequestType')
        department = HelpdeskDepartments.objects.values_list('department', flat=True).\
            filter(id=request.POST.get('department'))
        department = department[0]
        category = Categories.objects.values_list('title', flat=True).filter(id=request.POST.get('category'))
        category = category[0]
        sub_category = sub_categories.objects.values_list('title', flat=True).\
            filter(id=request.POST.get('sub_category'))
        sub_category = sub_category[0]
        priority = request.POST.get('priority')
        ticket_for = request.POST.get('yesno')
        on_behalf_of = request.POST.get('onBehalfOf')
        help_desk_office = HelpdeskOfficeLocation.objects.values_list('title',flat=True).\
            filter(id=request.POST.get('officeLocation'))
        help_desk_office = help_desk_office[0]
        desk_location = request.POST.get('deskLocation')
        files = request.FILES.get('documents')
        email_notification = request.POST.get('email_notification')

        try:
            item = HelpdeskRequestSLAs.objects.all().filter(HelpdeskCategory=category, HelpdeskDepartment=department,
                                                            HelpdeskPriority=priority,
                                                            HelpdeskSubCategory=sub_category)

            for i in item:
                TATHrs = i.TATHrs

            seconds = 0
            days = TATHrs / 8
            while TATHrs >= 8:
                seconds = seconds + 86400
                TATHrs = TATHrs - 8

            seconds = seconds + (TATHrs * 3600)

            a = 0
            for i in range(int(days)):

                dt1 = datetime.datetime.now() + timedelta(i + 1)
                if dt1.strftime("%A") == "Saturday":
                    a = a + 172800
            dt = datetime.datetime.now() + timedelta(seconds=a+seconds)
        except Exception as e:
            print(e)
            dt = ""
        if ticket_for == "OnBehalf":
            employee = EmployeeMaster.objects.values_list('reporting_to', 'empid', 'email').\
                filter(associated_user_account=on_behalf_of)
            try:
                on_behalf_user_employee_id = employee[0][1]
            except:
                messages.warning(request, 'Invalid employee name.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            OnBehalfUserEmployeeName = on_behalf_of
            Employee1 = EmployeeMaster.objects.values_list('associated_user_account', 'email').filter(empid=employee_id)
            EmployeeName = Employee1[0][0]
        else:
            employee = EmployeeMaster.objects.values_list('reporting_to', 'associated_user_account', 'email').\
                filter(empid=employee_id)
            EmployeeName = employee[0][1]
            OnBehalfUserEmployeeId = employee_id
            OnBehalfUserEmployeeName = EmployeeName
        FirstLevelApproverEmployeeName = employee[0][0]
        FirstApprover = EmployeeMaster.objects.values_list('empid', 'email').\
            filter(associated_user_account=FirstLevelApproverEmployeeName)
        FirstLevelApproverEmployeeId = FirstApprover[0][0]
        FirstApproverEmail = FirstApprover[0][1]
        form = HelpRequest(InActive=email_notification, RequestStatus="1", expected_closure=dt,
                           OnBehalfUserEmployeeId=OnBehalfUserEmployeeId,
                           OnBehalfUserEmployeeName=OnBehalfUserEmployeeName, WorkflowStatus="Workflow Initiated",
                           employee_id=employee_id, FirstLevelApproverEmployeeId=FirstLevelApproverEmployeeId,
                           FirstLevelApproverEmployeeName=FirstLevelApproverEmployeeName, EmployeeName=EmployeeName,
                           created_at=created_at, description=description, request_type=request_type,
                           department=department, category=category, sub_category=sub_category, priority=priority,
                           ticket_for=ticket_for, HelpdeskOffice=help_desk_office, DeskLocation=desk_location,
                           Files=files)
        try:
            form.save()
            key = 'HelpdeskTemplate_AssignTask'
            t_id = form.id
            form1 = WorkflowRequest(ActedByUser=OnBehalfUserEmployeeId, Process="Raised Ticket",
                                    ActedOn=str(datetime.datetime.now()), Action="Raised Ticket",
                                    Actor=OnBehalfUserEmployeeName, RequestStatus="Workflow Initiated",
                                    WorkflowPendingWith=FirstLevelApproverEmployeeName, RequestID_id=t_id)
            form1.save()
            form1 = WorkflowRequest(ActedByUser=FirstLevelApproverEmployeeId, Process="For First Approver",
                                    ActedOn=str(datetime.datetime.now()), Actor=FirstLevelApproverEmployeeName,
                                    RequestStatus="Pending", WorkflowPendingWith=FirstLevelApproverEmployeeName,
                                    RequestID_id=t_id)
            form1.save()
            if email_notification == "on":
                msg = "You have been assigned a service request for approval of which details are:"
                FirstApproverEmail = [FirstApproverEmail]
                email(key, t_id, FirstApproverEmail, msg)
                if ticket_for == "OnBehalf":
                    key = 'HelpdeskTemplate_InitiateWorkflow'
                    msg = "You have raised a service request on behalf of " + on_behalf_of + \
                          " for which the details are:"
                    to = [Employee1[0][1]]
                    email(key, t_id, to, msg)
                    key = 'HelpdeskTemplate_InitiateWorkflow'
                    msg = EmployeeName + " have raised a service request on behalf of you for which the details are:"
                    to = [employee[0][2]]
                    email(key, t_id, to, msg)
                else:
                    key = 'HelpdeskTemplate_InitiateWorkflow'
                    msg = "You have raised a service request of which the details are:"
                    to = [employee[0][2]]
                    email(key, t_id, to, msg)
            messages.warning(request, 'Ticket raised successfully')
            return HttpResponseRedirect('/main')
        except Exception as e:
            print(e)
            messages.warning(request, 'Something went wrong')
            return HttpResponseRedirect('/main')


def update_ticket(request, ticket_id):
    """
    To update ticket
    :param request: to update ticket if current status is pending
    :param ticket_id: id of ticket which is to be updated
    :return: to previous page
    """
    if request.method == "POST":
        item = HelpRequest.objects.get(pk=ticket_id)
        item.description = request.POST.get('Description')
        department = HelpdeskDepartments.objects.values_list('department', flat=True).\
            filter(id=request.POST.get('department'))
        item.department = department[0]
        category = Categories.objects.values_list('title', flat=True).filter(id=request.POST.get('category'))
        item.category = category[0]
        sub_category = sub_categories.objects.values_list('title', flat=True).\
            filter(id=request.POST.get('sub_category'))
        item.sub_category = sub_category[0]
        item.priority = request.POST.get('priority')
        HelpdeskOffice = HelpdeskOfficeLocation.objects.values_list('title', flat=True).\
            filter(id=request.POST.get('officeLocation'))
        item.HelpdeskOffice = HelpdeskOffice[0]
        item.DeskLocation = request.POST.get('deskLocation')
        item.Files = request.FILES.get('documents')
        item.InActive = request.POST.get('email_notification')
        item.save()
        if item.InActive == "on":
            key = "HelpdeskTemplate_UpdateTicket"
            msg = "Your ticket is updated successfully of which details are:"
            emailid = HelpRequest.objects.values_list('employee_id', flat=True).filter(id=ticket_id)
            Employee = EmployeeMaster.objects.values_list('email', flat=True).filter(empid=emailid[0])
            Employee = [Employee[0]]
            email(key, ticket_id, Employee, msg)
            key = "HelpdeskTemplate_UpdateTicket"
            msg = "Helpdesk ticket is updated of which details are:"
            emailid = HelpRequest.objects.values_list('FirstLevelApproverEmployeeId', flat=True).filter(id=ticket_id)
            Employee = EmployeeMaster.objects.values_list('email', flat=True).filter(empid=emailid[0])
            Employee = [Employee[0]]
            email(key, ticket_id, Employee, msg)
        return HttpResponseRedirect('/main')


def approve(request, ticket_id):
    """
    To activate ticket
    :param request: To approve ticket from first approver or manager
    :param ticket_id: id of ticket
    :return: to previous page
    """
    item1 = HelpRequest.objects.get(pk=ticket_id)
    item1.WorkflowStatus = "Activated"
    item1.WorkflowCurrentStatus = "Activated"
    item1.WorkflowModifiedOn = datetime.datetime.now()
    item1.save()
    item = WorkflowRequest.objects.get(RequestID_id=ticket_id, ActedByUser=request.session['username'],
                                       RequestStatus="Pending")
    item.RequestStatus = "Approved"
    if item1.department == "HR":
        item.WorkflowPendingWith = "Helpdesk HR Approver"
        roles = "HelpdeskHRApprover1"
    elif item1.department == "IT":
        item.WorkflowPendingWith = "Helpdesk IT Approver"
        roles = "HelpdeskITApprover1"
    elif(item1.department == "Admin"):
        item.WorkflowPendingWith = "Helpdesk Admin Approver"
        roles = "HelpdeskAdminApprover1"
    elif item1.department == "Finance":
        item.WorkflowPendingWith = "Helpdesk Finance Approver"
        roles = "HelpdeskFinanceApprover1"
    item.ActedOn = datetime.datetime.now()
    item.ActionData = request.GET.get('comments')
    item.save()
    form1 = WorkflowRequest(ActedOn=str(datetime.datetime.now()), Actor=item.WorkflowPendingWith,
                            RequestStatus="Pending", WorkflowPendingWith=item.WorkflowPendingWith,
                            Process="For Helpdesk Approver", RequestID_id=ticket_id)
    form1.save()
    if item1.InActive == "on":
        key = "HelpdeskTemplate_UpdateTicket"
        msg = "Your service request is approved by " + item1.EmployeeName + " of which details are:"
        emailid = HelpRequest.objects.values_list('OnBehalfUserEmployeeId', flat=True).filter(id=ticket_id)
        Employee = EmployeeMaster.objects.values_list('email', flat=True).filter(empid=emailid[0])
        Employee = [Employee[0]]
        email(key, ticket_id, Employee, msg)
        Employee = []
        key = "HelpdeskTemplate_AssignTask"
        msg = "You have been assigned a service request for approval of which details are:"
        user = AppList.objects.all().filter(roles=roles)
        for i in user:
            item = EmployeeMaster.objects.get(associated_user_account=i.user)
            Employee.append(item.email)
        email(key, ticket_id, Employee, msg)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def approve1(request, ticket_id):
    """
    To approve ticket
    :param request: To approve ticket from approver head
    :param ticket_id: id of ticket
    :return: to previous page
    """
    name = EmployeeMaster.objects.get(empid=request.session['username'])
    Approver=AppList.objects.all()
    for i in Approver:
        if i.user == name.associated_user_account and i.roles == "HelpdeskHRApprover1":
            item = WorkflowRequest.objects.get((Q(WorkflowPendingWith="Helpdesk HR Approver") |
                                                (Q(WorkflowPendingWith=name.associated_user_account))),
                                               RequestStatus="Pending", RequestID_id=ticket_id)
            item.WorkflowPendingWith = "Helpdesk Fullfiller Head HR"
            roles = "HelpdeskFulfillerHead_HR1"
        elif i.user == name.associated_user_account and i.roles == "HelpdeskITApprover1":
            item = WorkflowRequest.objects.get(RequestID_id=ticket_id, Actor="Helpdesk IT Approver",
                                               RequestStatus="Pending")
            item.WorkflowPendingWith = "Helpdesk Fullfiller Head IT"
            roles = "HelpdeskFulfillerHead_IT1"
        elif i.user == name.associated_user_account and i.roles == "HelpdeskAdminApprover1":
            item = WorkflowRequest.objects.get(RequestID_id=ticket_id, Actor="Helpdesk Admin Approver",
                                               RequestStatus="Pending")
            item.WorkflowPendingWith = "Helpdesk Fullfiller Head Admin"
            roles = "HelpdeskFulfillerHead_Admin1"

        elif i.user == name.associated_user_account and i.roles == "HelpdeskFinanceApprover1":
            item = WorkflowRequest.objects.get(RequestID_id=ticket_id, Actor="Helpdesk Finance Approver",
                                               RequestStatus="Pending")
            item.WorkflowPendingWith = "Helpdesk Fullfiller Head Finance"
            roles = "HelpdeskFulfillerHead_Finance1"
    item.RequestStatus = "Approved"
    item.ActedByUser = request.session['username']
    item.ActedOn = str(datetime.datetime.now())
    Actor = EmployeeMaster.objects.get(empid=request.session['username'])
    item.Actor = Actor.associated_user_account
    item.ActionData = request.GET.get('comments')
    item.save()
    form1 = WorkflowRequest(ActedOn=str(datetime.datetime.now()), Process="For Helpdesk Fulfiller Head",
                            Actor=item.WorkflowPendingWith, RequestStatus="Pending",
                            WorkflowPendingWith=item.WorkflowPendingWith, RequestID_id=ticket_id)
    form1.save()
    item1 = HelpRequest.objects.get(pk=ticket_id)
    if item1.InActive == "on":
        key = "HelpdeskTemplate_UpdateTicket"
        msg = "Your service request is approved by " + item.Actor + " of which details are:"
        emailid = HelpRequest.objects.values_list('OnBehalfUserEmployeeId', flat=True).filter(id=ticket_id)
        Employee = EmployeeMaster.objects.values_list('email', flat=True).filter(empid=emailid[0])
        Employee = [Employee[0]]
        email(key, ticket_id, Employee, msg)
        Employee = []
        key = "HelpdeskTemplate_AssignTask"
        msg = "You have been assigned a service request of which details are:"
        user = AppList.objects.all().filter(roles=roles)
        for i in user:
            item = EmployeeMaster.objects.get(associated_user_account=i.user)
            Employee.append(item.email)
        email(key, ticket_id, Employee, msg)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def reject(request, ticket_id):
    """
    To reject ticket
    :param request: to reject ticket from first approver or manager
    :param ticket_id: id of ticket which is to be rejected
    :return: to previous page
    """
    item = HelpRequest.objects.get(pk=ticket_id)
    item.WorkflowStatus = "Rejected"
    item.WorkflowCurrentStatus = "Rejected"
    item.save()
    item1 = WorkflowRequest.objects.get(RequestID_id=ticket_id, RequestStatus="Pending")
    item1.RequestStatus = "Rejected"
    item1.ActionData = request.GET.get('comments')
    item1.save()
    if item.InActive == "on":
        key = "HelpdeskTemplate_UpdateTicket"
        msg = "Your service request is rejected of which details are:"
        emailid = HelpRequest.objects.values_list('OnBehalfUserEmployeeId', flat=True).filter(id=ticket_id)
        Employee = EmployeeMaster.objects.values_list('email', flat=True).filter(empid=emailid[0])
        Employee = [Employee[0]]
        email(key, ticket_id, Employee, msg)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def reject1(request, ticket_id):
    """
    To reject ticket
    :param request: to reject ticket from approver head
    :param ticket_id: id of ticket which is to be rejected
    :return: to previous page
    """
    item = HelpRequest.objects.get(pk=ticket_id)
    item.WorkflowStatus = "Rejected"
    item.WorkflowCurrentStatus = "Rejected"
    item.save()
    item1 = WorkflowRequest.objects.get(RequestID_id=ticket_id, RequestStatus="Pending")
    item1.RequestStatus = "Rejected"
    item1.save()
    if item.InActive == "on":
        key = "HelpdeskTemplate_UpdateTicket"
        msg = "Your service request is rejected of which details are:"
        emailid = HelpRequest.objects.values_list('OnBehalfUserEmployeeId', flat=True).filter(id=ticket_id)
        Employee = EmployeeMaster.objects.values_list('email', flat=True).filter(empid=emailid[0])
        Employee = [Employee[0]]
        email(key, ticket_id, Employee, msg)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def display(request, ticket_id):
    """
    To display ticket
    :param request:To view ticket details
    :param ticket_id:id of ticket
    :return: to display.html to view ticket details
    """
    try:
        user, SLAFullfillerHead, FirstApprover, ApproverHead, FulfillerHead, Fulfiller = fulfiller(request)
    except Exception as e:
        print(e)
        return redirect('home')
    item = HelpRequest.objects.get(pk=ticket_id)
    emp1 = ""
    try:
        emp = request.session['username']
        empName = EmployeeMaster.objects.get(empid=emp)
        empName = empName.associated_user_account
    except Exception as e:
        print(e)
        return HttpResponseRedirect('/home')
    Approver = AppList.objects.all()
    for i in Approver:
        if i.user == empName and i.roles == "HelpdeskHRApprover1":
            emp1 = "Helpdesk HR Approver"     
        elif i.user == empName and i.roles == "HelpdeskITApprover1":
            emp1 = "Helpdesk IT Approver"
                
        elif i.user == empName and i.roles == "HelpdeskAdminApprover1":
            emp1 = "Helpdesk Admin Approver"
                
        elif i.user == empName and i.roles == "HelpdeskFinanceApprover1":
            emp1 = "Helpdesk Finance Approver"
    try:
        workflow = WorkflowRequest.objects.get((Q(RequestStatus="Pending") |
                                                (Q(RequestStatus="Completed", Process="Complete"))),
                                               RequestID_id=ticket_id)
        workflow1 = WorkflowRequest.objects.all().filter(Action="Raised Query", RequestID_id=ticket_id)
        return render(request, "display.html", {'media_url': settings.MEDIA_URL, 'Fulfiller': Fulfiller, 'user': user,
                                                'SLAFulfillerHead': SLAFullfillerHead, 'FirstApprover': FirstApprover,
                                                'ApproverHead': ApproverHead, 'FulfillerHead': FulfillerHead,
                                                'item': item, 'workflow1': workflow1, 'emp': empName,
                                                'workflow': workflow, 'emp1': emp1})
    except:
        return render(request, "display.html", {'media_url': settings.MEDIA_URL, 'Fulfiller': Fulfiller, 'user': user,
                                                'SLAFulfillerHead': SLAFullfillerHead, 'FirstApprover': FirstApprover,
                                                'ApproverHead': ApproverHead, 'FulfillerHead': FulfillerHead,
                                                'item': item, 'emp': empName, 'emp1': emp1})


def workflow(request, ticket_id):
    """
        To display workflow of ticket
        :param request:To view workflow of ticket in details
        :param ticket_id:id of ticket
        :return: to details of workflow
    """
    workflow = WorkflowRequest.objects.all().filter(RequestID_id=ticket_id).order_by('ActedOn')
    user, SLAFullfillerHead, FirstApprover, ApproverHead, FulfillerHead, Fulfiller = fulfiller(request)
    return render(request, "workflow.html", {'Fulfiller': Fulfiller, 'user': user,
                                             'SLAFulfillerHead': SLAFullfillerHead, 'FirstApprover': FirstApprover,
                                             'ApproverHead': ApproverHead, 'FulfillerHead': FulfillerHead,
                                             'workflow': workflow})


def assign(request, ticket_id):
    """
    Sends data of Fulfillers from fulfiller group
    :param request: Sends data of Fulfillers from fulfiller group foe particular ticket
    :param ticket_id:id of ticket
    :return: to assign.html with details of fulfillers list
    """
    name = EmployeeMaster.objects.get(empid=request.session['username'])
    approver_list = AppList.objects.all()
    for approver in approver_list:
        if approver.user == name.associated_user_account and approver.roles == "HelpdeskFulfillerHead_HR1":
            all_items = HelpdeskFulfillerGroups.objects.all().filter(group_name="HR")
        elif approver.user == name.associated_user_account and approver.roles == "HelpdeskFulfillerHead_IT1":
            all_items = HelpdeskFulfillerGroups.objects.all().filter(group_name="IT")
        elif approver.user == name.associated_user_account and approver.roles == "HelpdeskFulfillerHead_Admin1":
            all_items = HelpdeskFulfillerGroups.objects.all().filter(group_name="Admin")
        elif approver.user == name.associated_user_account and approver.roles == "HelpdeskFulfillerHead_Finance1":
            all_items = HelpdeskFulfillerGroups.objects.all().filter(group_name="Finance")
    user, SLAFullfillerHead, FirstApprover, ApproverHead, FulfillerHead, Fulfiller = fulfiller(request)
    return render(request, "assign.html", {'Fulfiller': Fulfiller, 'user': user, 'SLAFulfillerHead': SLAFullfillerHead,
                                           'FirstApprover': FirstApprover, 'ApproverHead': ApproverHead,
                                           'FulfillerHead': FulfillerHead, 'all_items': all_items,
                                           'ticket_id': ticket_id})


def assign_ticket(request, ticket_id):
    """
    Assigns ticket for fulfillment
    :param request: to assign a ticket to particular fulfiller
    :param ticket_id: id of ticket
    :return: to previous page
    """
    name = EmployeeMaster.objects.get(empid=request.session['username'])
    approver = AppList.objects.all()
    for i in approver:
        if i.user == name.associated_user_account and i.roles == "HelpdeskFulfillerHead_HR1":
            item = WorkflowRequest.objects.get(RequestID_id=ticket_id, Actor="Helpdesk Fullfiller Head HR",
                                               RequestStatus="Pending")
        elif i.user == name.associated_user_account and i.roles == "HelpdeskFulfillerHead_IT1":
            item = WorkflowRequest.objects.get(RequestID_id=ticket_id, Actor="Helpdesk Fullfiller Head IT",
                                               RequestStatus="Pending")

        elif i.user == name.associated_user_account and i.roles == "HelpdeskFulfillerHead_Admin1":
            item = WorkflowRequest.objects.get(RequestID_id=ticket_id, Actor="Helpdesk Fullfiller Head Admin",
                                               RequestStatus="Pending")
            
        elif i.user == name.associated_user_account and i.roles == "HelpdeskFulfillerHead_Finance1":
            item = WorkflowRequest.objects.get(RequestID_id=ticket_id, Actor="Helpdesk Fullfiller Head Finance",
                                               RequestStatus="Pending")
    item.RequestStatus = "Assigned"
    item.ActedByUser = request.session['username']
    item.ActedOn = str(datetime.datetime.now())
    actor = EmployeeMaster.objects.get(empid=request.session['username'])
    item.ActionData = request.POST.get('comments')
    item.Actor = actor.associated_user_account
    assign_to = request.POST.get('assignTo')
    assign_to = EmployeeMaster.objects.get(empid=assign_to)
    assign_to_name = assign_to.associated_user_account
    item1 = HelpRequest.objects.get(id=ticket_id)
    form1 = WorkflowRequest(ActedByUser=assign_to.empid, Process="Complete", ActedOn=str(datetime.datetime.now()),
                            Actor=assign_to_name, RequestStatus="Pending", WorkflowPendingWith=assign_to_name,
                            RequestID_id=ticket_id)
    form1.save()
    item.save()
    if item1.InActive == "on":    
        key = "HelpdeskTemplate_UpdateTicket"
        msg = "Your service request is assigned to "+assign_to_name+" of which details are:"
        emailid = HelpRequest.objects.values_list('OnBehalfUserEmployeeId', flat=True).filter(id=ticket_id)
        Employee = EmployeeMaster.objects.values_list('email', flat=True).filter(empid=emailid[0])
        Employee = [Employee[0]]
        email(key, ticket_id, Employee, msg)
        key = "HelpdeskTemplate_AssignTask"
        msg = "You have been assigned a service request for fulfillment of which details are:"
        employee = [assign_to.email]
        email(key, ticket_id, employee, msg)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def update(request,ticket_id):
    """
    Provide data for update ticket
    :param request: to send data of ticket which is to be updated
    :param ticket_id: id of ticket
    :return: to raiseTicket.html with data to update
    """""
    try:
        user, SLAFullfillerHead, FirstApprover, ApproverHead, FulfillerHead, Fulfiller = fulfiller(request)
    except:
        return redirect('home')
    item = HelpRequest.objects.get(pk=ticket_id)
    officelocation = HelpdeskOfficeLocation.objects.all()
    departments = HelpdeskDepartments.objects.all().filter(request_type="Request")
    category = Categories.objects.all()
    subCategory = sub_categories.objects.all()
    employee = EmployeeMaster.objects.all()
    firstApprover = EmployeeMaster.objects.values_list('reporting_to', flat=True).\
        filter(empid=request.session['username'])
    firstApprover = firstApprover[0]
    return render(request, "raiseTicket.html", {'firstApprover': firstApprover, 'Fulfiller': Fulfiller, 'user': user,
                                                'SLAFulfillerHead': SLAFullfillerHead, 'FirstApprover': FirstApprover,
                                                'ApproverHead': ApproverHead, 'FulfillerHead': FulfillerHead,
                                                'employee': employee, 'item': item, 'subCategory': subCategory,
                                                'officelocation': officelocation, 'departments': departments,
                                                'category': category})


def log(request):
    """Returns to main page for invalid credentials"""
    return render(request, "login.html", {})


def raise_ticket(request):
    """
    Sends data required to raise a ticket
    :param request: to provide data to raise ticket
    :return: to raiseTicket.html with data
    """
    try:
        user, SLAFullfillerHead, FirstApprover, ApproverHead, FulfillerHead, Fulfiller = fulfiller(request)
    except:
        return redirect('home')
    officelocation = HelpdeskOfficeLocation.objects.all()
    departments = HelpdeskDepartments.objects.all().filter(request_type="Request")
    category = Categories.objects.all()
    subCategory = sub_categories.objects.all()
    firstApprover = EmployeeMaster.objects.values_list('reporting_to', flat=True).\
        filter(empid=request.session['username'])
    firstApprover = firstApprover[0]
    employee = EmployeeMaster.objects.all()
    return render(request, "raiseTicket.html", {'Fulfiller': Fulfiller, 'user': user,
                                                'SLAFulfillerHead': SLAFullfillerHead, 'FirstApprover': FirstApprover,
                                                'ApproverHead': ApproverHead, 'FulfillerHead': FulfillerHead,
                                                'employee': employee, 'firstApprover': firstApprover,
                                                'subCategory': subCategory, 'officelocation': officelocation,
                                                'departments': departments, 'category': category})


def raise_query(request, ticket_id):
    """
    Raise Query
    :param request: to raise a query (for first approver/manage and helpdesk approver  head)
    :param ticket_id:
    :return:
    """
    item = HelpRequest.objects.get(id=ticket_id)
    item.WorkflowStatus = "Raised Query"
    name = EmployeeMaster.objects.get(empid=request.session['username'])
    item.save()
    try:
        item1 = WorkflowRequest.objects.get((Q(Process="For First Approver") | Q(Process="For Helpdesk Approver")),
                                            RequestID_id=ticket_id, ActedByUser=request.session['username'],
                                            RequestStatus="Pending")
    except:
        Approver = AppList.objects.all()
        for i in Approver:
            if i.user == name.associated_user_account and i.roles == "HelpdeskHRApprover1":
                item1 = WorkflowRequest.objects.get((Q(WorkflowPendingWith="Helpdesk HR Approver") |
                                                     (Q(WorkflowPendingWith=name.associated_user_account))),
                                                    RequestStatus="Pending", Process="For Helpdesk Approver",
                                                    RequestID_id=ticket_id)
            elif i.user == name.associated_user_account and i.roles == "HelpdeskITApprover1":
                item1 = WorkflowRequest.objects.get(RequestID_id=ticket_id, Actor="Helpdesk IT Approver",
                                                    RequestStatus="Pending")
            elif i.user == name.associated_user_account and i.roles == "HelpdeskAdminApprover1":
                item1 = WorkflowRequest.objects.get(RequestID_id=ticket_id, Actor="Helpdesk Admin Approver",
                                                    RequestStatus="Pending")
            elif i.user == name.associated_user_account and i.roles == "HelpdeskFinanceApprover1":
                item1 = WorkflowRequest.objects.get(RequestID_id=ticket_id, Actor="Helpdesk Finance Approver",
                                                    RequestStatus="Pending")
    item1.Action = "Raised Query"         
    item1.RequestStatus = "Raised Query"
    item1.ActedOn = str(datetime.datetime.now())
    item1.ActionData = request.GET.get('comments')
    item1.ActedByUser = name.empid
    item1.Actor = name.associated_user_account
    item1.WorkflowPendingWith = name.associated_user_account
    item1.save()
    form = WorkflowRequest(ActedByUser=item.OnBehalfUserEmployeeId, Process="Answer Query",
                           ActedOn=str(datetime.datetime.now()), Actor=item.OnBehalfUserEmployeeName,
                           RequestStatus="Pending", WorkflowPendingWith=item.OnBehalfUserEmployeeName,
                           RequestID_id=ticket_id)
    form.save()
    if item.InActive == "on":
        key = "HelpdeskTemplate_AssignTask"
        msg = name.associated_user_account + " raised a query for ticket of which details are:"
        email_id = HelpRequest.objects.values_list('OnBehalfUserEmployeeId', flat=True).filter(id=ticket_id)
        employee = EmployeeMaster.objects.values_list('email', flat=True).filter(empid=email_id[0])
        employee = [employee[0]]
        email(key, ticket_id, employee, msg)
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def cancel(request, ticket_id):
    """
    Cancel Request manually
    :param request: to cancel a ticket
    :param ticket_id: id of ticket
    :return: to previous page
    """
    item = HelpRequest.objects.get(id=ticket_id)
    item.WorkflowStatus = "Cancel"
    item.WorkflowCurrentStatus = "Cancel"
    item.save()
    item1 = WorkflowRequest.objects.get(RequestID_id=ticket_id, RequestStatus="Pending")
    item1.RequestStatus = "Incomplete"
    item1.save()
    form = WorkflowRequest(ActedByUser=request.session['username'], Process="Cancel",
                           ActedOn=str(datetime.datetime.now()), Actor=item.OnBehalfUserEmployeeName,
                           RequestStatus="Cancelled", RequestID_id=ticket_id)
    form.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def ans_query(request, ticket_id):
    """
    Answer query
    :param request: to answer a query for ticket
    :param ticket_id: id of ticket
    :return: to previous page
    """
    item = HelpRequest.objects.get(id=ticket_id)
    item.WorkflowStatus = item.WorkflowCurrentStatus
    item1 = WorkflowRequest.objects.get(RequestID_id=ticket_id, ActedByUser=request.session['username'],
                                        RequestStatus="Pending")
    item1.RequestStatus = "Answered Query"
    item1.ActedOn = str(datetime.datetime.now())
    item1.ActionData = request.GET.get('comments')
    item2 = WorkflowRequest.objects.get(Action="Raised Query", RequestStatus="Raised Query", RequestID_id=ticket_id)
    item.save()
    item1.save()
    form = WorkflowRequest(ActedByUser=item2.ActedByUser, Process=item2.Process, ActedOn=str(datetime.datetime.now()),
                           Actor=item2.Actor, RequestStatus="Pending", WorkflowPendingWith=item2.Actor,
                           RequestID_id=ticket_id)
    form.save()
    item2.Action = "Raise Query"
    item2.save()
    if item.InActive == "on":
        key = "HelpdeskTemplate_AssignTask"
        msg = item.OnBehalfUserEmployeeName + " answered a query for ticket of which details are:"
        employee = EmployeeMaster.objects.values_list('email', flat=True).filter(empid=item2.ActedByUser)
        employee = [employee[0]]
        email(key, ticket_id, employee, msg)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def reopen(request, ticket_id):
    """
    Reopen ticket after completion
    :param request: to reopen ticket
    :param ticket_id: id of ticket
    :return: to previous page
    """
    item = WorkflowRequest.objects.get(RequestID_id=ticket_id, RequestStatus="Completed", Process="Complete")
    item.Process = "Reopened"
    item.save()
    item1 = HelpRequest.objects.get(id=ticket_id)
    item1.WorkflowStatus = "Reopened"
    item1.WorkflowCurrentStatus = "Reopened"
    item1.save()
    comments = request.GET.get('comments')
    form1 = WorkflowRequest(ActionData=comments, ActedByUser=request.session['username'], Process="Reopen",
                            ActedOn=str(datetime.datetime.now()), Actor=item1.OnBehalfUserEmployeeName,
                            RequestStatus="Reopened", WorkflowPendingWith=item.Actor, RequestID_id=ticket_id)
    form1.save()
    form = WorkflowRequest(ActedByUser=item.ActedByUser, ActedOn=str(datetime.datetime.now()), Actor=item.Actor,
                           Process="Complete", RequestStatus="Pending", WorkflowPendingWith=item.Actor,
                           RequestID_id=ticket_id)
    form.save()
    if item1.InActive == "on":
        key = "HelpdeskTemplate_AssignTask"
        msg = item1.OnBehalfUserEmployeeName + " reopened ticket of which details are:"
        employee = EmployeeMaster.objects.values_list('email', flat=True).filter(empid=item.ActedByUser)
        employee = [employee[0]]
        email(key, ticket_id, employee, msg)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))   


def Close(request, ticket_id):
    """
    Close ticket after completion
    :param request: close ticket
    :param ticket_id: id of ticket
    :return: to previous page
    """
    item = HelpRequest.objects.get(id=ticket_id)
    item.WorkflowStatus = "Closed"
    item.WorkflowCurrentStatus = "Closed"
    item.save()
    item1 = WorkflowRequest.objects.get(RequestID_id=ticket_id, RequestStatus="Completed", Process="Complete")
    item1.Process = "Closed"
    item1.save()
    comments = request.GET.get('comments')
    form1 = WorkflowRequest(ActionData=comments, ActedByUser=request.session['username'], Process="Close",
                            ActedOn=str(datetime.datetime.now()), Actor=item.OnBehalfUserEmployeeName,
                            RequestStatus="Closed", RequestID_id=ticket_id)
    form1.save()
    if item.InActive == "on":
        key = "HelpdeskTemplate_AssignTask"
        msg = "You closed a service ticket of which details are:"
        emailid = HelpRequest.objects.values_list('OnBehalfUserEmployeeId', flat=True).filter(id=ticket_id)
        employee = EmployeeMaster.objects.values_list('email', flat=True).filter(empid=emailid[0])
        employee = [employee[0]]
        email(key, ticket_id, employee, msg)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))   


def logout(request):
    """
    Logout
    """
    request.session.flush()
    if hasattr(request, 'user'):
        request.user = AnonymousUser()
    return redirect('home')


def sla(request):
    """
    Display SLA's using bootstrap paginator
    :param request: to display SLA's
    :return:
    """
    try:
        user, SLAFullfillerHead, FirstApprover, ApproverHead, FulfillerHead, Fulfiller = fulfiller(request)
    except:
        return redirect('home')
    all_items = HelpdeskRequestSLAs.objects.all().order_by('HelpdeskDepartment', 'HelpdeskCategory',
                                                           'HelpdeskSubCategory')
    return render(request, "pagination.html", {'Fulfiller': Fulfiller, 'user': user,
                                               'SLAFulfillerHead': SLAFullfillerHead, 'FirstApprover': FirstApprover,
                                               'ApproverHead': ApproverHead, 'FulfillerHead': FulfillerHead,
                                               'all_items': all_items})
    

def slas(request, ticket_id):
    """
    Returns data for editing or adding SLA
    :param request: to provide data
    :param ticket_id: id of SLA's
    :return:
    """
    officelocation = HelpdeskOfficeLocation.objects.all()
    departments = HelpdeskDepartments.objects.all().filter(request_type="Request")
    category = Categories.objects.all()
    sub_category = sub_categories.objects.all()
    employee = EmployeeMaster.objects.all()
    try:
        ticket_id = HelpdeskRequestSLAs.objects.get(pk=ticket_id)
        return render(request, "edit_sla.html", {'ticket': ticket_id, 'employee': employee, 'subCategory': sub_category,
                                                 'officelocation': officelocation, 'departments': departments,
                                                 'category': category})
    except:
        return render(request, "edit_sla.html", {'employee': employee, 'subCategory': sub_category,
                                                 'officelocation': officelocation, 'departments': departments,
                                                 'category': category})


def edit_sla(request, ticket_id):
    """
    Edit SLA
    :param request: to edit SLA
    :param ticket_id: id of SLA
    :return:
    """
    item = HelpdeskRequestSLAs.objects.get(pk=ticket_id)
    item.TATHrs = request.POST.get('TATHrs')
    item.TATMins = request.POST.get('TATMins')
    item.EM_0_AfterHrs = request.POST.get('EM_0_AfterHrs')
    item.EM_1_AfterHrs = request.POST.get('EM_1_AfterHrs')    
    item.EM_0_AfterMin = request.POST.get('EM_0_AfterMin')
    item.EM_1_AfterMin = request.POST.get('EM_1_AfterMin')
    item.EM_0_Name = request.POST.get('EM_0_Name')
    item.EM_1_Name = request.POST.get('EM_1_Name')
    em_zero_to = EmployeeMaster.objects.values_list('empid', flat=True).\
        filter(associated_user_account=request.POST.get('EM_0_Name'))
    em_one_to = EmployeeMaster.objects.values_list('empid', flat=True).\
        filter(associated_user_account=request.POST.get('EM_1_Name'))
    try:
        print(em_zero_to[0],em_one_to[0])
    except:
        messages.warning(request, 'Invalid employee name.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    item.EM_1_To = em_one_to[0]
    item.EM_0_To = em_zero_to[0]
    item.save()
    messages.warning(request, 'Successfully Edited')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def add_sla(request):
    """
    Add SLA
    :param request: to add new SLA
    :return:
    """
    help_desk_location = request.POST.get('location')
    department = HelpdeskDepartments.objects.values_list('department', flat=True).\
        filter(id=request.POST.get('department'))
    help_desk_department = department[0]
    category = Categories.objects.values_list('title', flat=True).filter(id=request.POST.get('category'))
    help_desk_category = category[0]
    sub_category = sub_categories.objects.values_list('title', flat=True).filter(id=request.POST.get('sub_category'))
    help_desk_sub_category = sub_category[0]
    help_desk_priority = request.POST.get('priority')
    try:
        HelpdeskRequestSLAs.objects.get(HelpdeskDepartment=help_desk_department, HelpdeskCategory=help_desk_category,
                                        HelpdeskSubCategory=help_desk_sub_category, HelpdeskPriority=help_desk_priority)
        messages.warning(request, 'This SLA already exists. You can edit it.')
    except: 
        total_hrs = request.POST.get('TATHrs')
        total_mins = request.POST.get('TATMins')
        em_zero_after_hrs = request.POST.get('EM_0_AfterHrs')
        em_one_after_hrs = request.POST.get('EM_1_AfterHrs') 
        em_zero_after_mins = request.POST.get('EM_0_AfterMin')
        em_one_after_mins = request.POST.get('EM_1_AfterMin')
        em_zero_name = request.POST.get('EM_0_Name')
        em_one_name = request.POST.get('EM_1_Name')
        em_zero_to = EmployeeMaster.objects.values_list('empid', flat=True).\
            filter(associated_user_account=request.POST.get('EM_0_Name'))
        em_one_to = EmployeeMaster.objects.values_list('empid', flat=True).\
            filter(associated_user_account=request.POST.get('EM_1_Name'))
        try:
            print(em_zero_to[0], em_one_to[0])
        except:
            messages.warning(request, 'Invalid employee name.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        em_one_to = em_one_to[0]
        em_zero_to = em_zero_to[0]
        form = HelpdeskRequestSLAs(EM_0_AfterHrs=em_zero_after_hrs, EM_0_AfterMin=em_zero_after_mins,
                                   EM_0_Name=em_zero_name, EM_0_To=em_zero_to, EM_1_AfterHrs=em_one_after_hrs,
                                   EM_1_AfterMin=em_one_after_mins, EM_1_Name=em_one_name, EM_1_To=em_one_to,
                                   HelpdeskCategory=help_desk_category, HelpdeskDepartment=help_desk_department,
                                   HelpdeskLocation=help_desk_location, HelpdeskPriority=help_desk_priority,
                                   HelpdeskSubCategory=help_desk_sub_category, TATHrs=total_hrs, TATMins=total_mins)
        form.save()
        messages.warning(request, 'Successfully Added')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def delete_sla(request, ticket_id):
    """
    Delete SLA
    :param request: Delete SLA
    :param ticket_id: id of SLA
    :return:
    """
    item = HelpdeskRequestSLAs.objects.get(pk=ticket_id)
    item.delete()
    messages.warning(request, 'Successfully Deleted')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def view_document(request, name):
    """
    Display documnets
    :param request: display documents from database
    :param name: name of file stored in database
    :return:
    """
    name = "media/Documents/" + name
    webbrowser.open('file://' + os.path.realpath(name))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def view_employees(request):
    """
    Get all employees
    :param request: Display employees from employee master
    :return: to employee.html
    """
    pass
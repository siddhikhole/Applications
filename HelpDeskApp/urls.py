from django.conf.urls import url
from HelpDeskApp import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

app_name = 'HelpDeskApp'
urlpatterns = [
                url(r'^home/$', views.home, name='home'),
                url(r'^HelpDeskApp/gettoken/$', views.gettoken, name='gettoken'),
                path('view_Report', views.view_report, name="view_report"),
                path('view_document/Documents/<name>', views.view_document, name="view_document"),
                path('add_sla', views.add_sla, name="add_sla"),
                path('delete_sla/<ticket_id>', views.delete_sla, name="delete_sla"),
                path('edit_sla/<ticket_id>', views.edit_sla, name="edit_sla"),
                path('slas/<ticket_id>', views.slas, name="slas"),
                path('sla/', views.sla, name="sla"),
                path('raiseTicket/addTicket/', views.add_ticket, name="add_ticket"),
                path('update/<ticket_id>/updateTicket', views.update_ticket, name="update_ticket"),
                path('raiseTicket/', views.raise_ticket, name="raise_ticket"),
                path('update/<ticket_id>/', views.update, name="update"),
                path('cancel/<ticket_id>/', views.cancel, name="cancel"),
                path('approve/<ticket_id>', views.approve, name="approve"),
                path('approve1/<ticket_id>', views.approve1, name="approve1"),
                path('display/<ticket_id>', views.display, name="display"),
                path('workflow/<ticket_id>',views.workflow,name="workflow"),
                path('assign/<ticket_id>',views.assign,name="assign"),
                path('assignTicket/<ticket_id>',views.assign_ticket,name="assign_ticket"),
                path('main/',views.main,name="main"),
                path('logout/',views.logout,name="logout"),
                path('reject/<ticket_id>',views.reject,name="reject"),
                path('reject1/<ticket_id>',views.reject1,name="reject1"),
                path('complete/<ticket_id>',views.complete,name="complete"),
                path('raiseQuery/<ticket_id>',views.raise_query,name="raise_query"),
                path('answer/<ticket_id>',views.ans_query,name="ans_query"),
                path('pending/',views.pending,name="pending"),
                path('approved/',views.approved,name="approved"),
                path('completed/',views.completed,name="completed"),
                path('reopened/',views.reopened,name="reopened"),
                path('raisedQ/',views.raised_query, name="raised_query"),
                path('closed/', views.closed,name="closed"),
                path('cancelled/', views.cancelled, name="cancelled"),
                path('approval/', views.approval, name="approval"),
                path('rejected/',views.rejected,name="rejected"),
                path('AssignedTickets/',views.assigned_tickets, name="assigned_tickets"),
                path('HelpdeskApprover/',views.help_desk_approve, name="help_desk_approve"),
                path('HelpdeskFulfillerHead/', views.help_desk_ful_filler_head, name="help_desk_ful_filler_head"),
                path('Report/', views.report, name="report"),
                path('reopen/<ticket_id>', views.reopen, name="reopen"),
                path('close/<ticket_id>', views.close, name="close"),
                path('view_employee', views.view_employees, name="view_employee"),
                path('get_employee_details/<ticket_id>', views.get_employee_details, name="get_employee_details"),
                path('edit_employee/<emp_id>', views.edit_employee, name="edit_employee")
                ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

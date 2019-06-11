from django.conf.urls import url
from HelpDeskApp import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

app_name = 'tutorial'
urlpatterns = [
  # The home view ('/tutorial/')
  url(r'^$', views.home, name='home'),
  # Explicit home ('/tutorial/home/')
  url(r'^home/$', views.home, name='home'),
  # Redirect to get token ('/tutorial/gettoken/')
  url(r'^HelpDeskApp/gettoken/$', views.gettoken, name='gettoken'),
 path('view_Report',views.view_Report,name="view_Report"),
 
 path('view_document/Documents/<name>',views.view_document,name="view_document"),
path('add_sla',views.add_sla,name="add_sla"),
path('delete_sla/<ticket_id>',views.delete_sla,name="delete_sla"),
path('edit_sla/<ticket_id>',views.edit_sla,name="edit_sla"),
path('slas/<ticket_id>',views.slas,name="slas"),
path('sla/',views.sla,name="sla"),
path('raiseTicket/addTicket/',views.addTicket,name="addTicket"),
path('update/<ticket_id>/updateTicket',views.updateTicket,name="updateTicket"),
path('raiseTicket/',views.raiseTicket,name="raiseTicket"),
path('update/<ticket_id>/',views.update,name="update"),
path('cancel/<ticket_id>/',views.cancel,name="cancel"),
path('approve/<ticket_id>',views.approve,name="approve"),
path('approve1/<ticket_id>',views.approve1,name="approve1"),
path('display/<ticket_id>',views.display,name="display"),
path('workflow/<ticket_id>',views.workflow,name="workflow"),
path('assign/<ticket_id>',views.assign,name="assign"),
path('assignTicket/<ticket_id>',views.assignTicket,name="assignTicket"),
path('main/',views.main,name="main"),
path('logout/',views.logout,name="logout"),
path('reject/<ticket_id>',views.reject,name="reject"),
path('reject1/<ticket_id>',views.reject1,name="reject1"),
path('complete/<ticket_id>',views.complete,name="complete"),
path('raiseQuery/<ticket_id>',views.raiseQuery,name="raiseQuery"),
path('answer/<ticket_id>',views.ansQuery,name="ansQuery"),
path('pending/',views.pending,name="pending"),
path('approved/',views.approved,name="approved"),
path('completed/',views.completed,name="completed"),
path('reopened/',views.reopened,name="reopened"),
path('raisedQ/',views.raisedQ,name="raisedQ"),
path('closed/',views.closed,name="closed"),
path('cancelled/',views.cancelled,name="cancelled"),
path('approval/',views.approval,name="approval"),
path('rejected/',views.rejected,name="rejected"),
path('AssignedTickets/',views.AssignedTickets,name="AssignedTickets"),
path('HelpdeskApprover/',views.HelpdeskApprover,name="HelpdeskApprover"),
path('HelpdeskFulfillerHead/',views.HelpdeskFulfillerHead,name="HelpdeskFulfillerHead"),
path('Report/',views.Report,name="Report"),
path('reopen/<ticket_id>',views.Reopen,name="Reopen"),
path('close/<ticket_id>',views.Close,name="Close")
] + static(settings.MEDIA_URL , document_root = settings.MEDIA_ROOT)

from django.conf.urls import url
from HelpDeskApp import views
from django.urls import path

app_name = 'tutorial'
urlpatterns = [
  # The home view ('/tutorial/')
  url(r'^$', views.home, name='home'),
  # Explicit home ('/tutorial/home/')
  url(r'^home/$', views.home, name='home'),
  # Redirect to get token ('/tutorial/gettoken/')
  url(r'^HelpDeskApp/gettoken/$', views.gettoken, name='gettoken'),


path('raiseTicket/addTicket/',views.addTicket,name="addTicket"),
path('update/<ticket_id>/updateTicket',views.updateTicket,name="updateTicket"),
path('raiseTicket/',views.raiseTicket,name="raiseTicket"),
path('delete/<ticket_id>/',views.delete,name="delete"),
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

]
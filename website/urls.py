from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', views.logout_user, name='logout'),
    path('compose/', views.compose, name='compose'),
    path('personalize/', views.personalize, name='personalize'),
    path('contacts/', views.contacts, name='contacts'),
    path('sent/', views.sent, name='sent'),
    # path('template/', views.template, name='template'),
    path('top_up/', views.top_up, name='top_up'),
    path('drafts/', views.drafts, name='drafts'),
    
]
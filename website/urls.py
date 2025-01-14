from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("logout/", views.logout_user, name="logout"),
    path("compose/", views.compose, name="compose"),
    path("personalize/", views.personalize, name="personalize"),
    path("contacts/", views.contacts, name="contacts"),
    path("sent/", views.sent, name="sent"),
    path('template/', views.template, name='template'),
    path("top_up/", views.top_up, name="top_up"),
    path("drafts/", views.drafts_list, name="drafts_list"),
    path("drafts/edit/<int:draft_id>/", views.edit_draft, name="edit_draft"),
    path("drafts/delete/<int:draft_id>/", views.delete_draft, name="delete_draft"),
]

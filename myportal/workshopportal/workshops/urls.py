# filepath: /c:/WorkshopPortal_local/myportal/workshopportal/workshops/urls.py
from django.urls import path, include
from . import views

urlpatterns = [
    path('workshops/', views.list_workshops, name='workshops'),
    path('students/', views.students_permission, name='students_permission'),
    path('add_workshop/', views.add_workshops, name='add_workshops'),
]
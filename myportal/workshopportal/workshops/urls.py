from django.urls import path, include
from . import views

urlpatterns = [
    path('workshops/', views.list_workshops, name='workshops'),
    path('students/', views.students_permission, name='students_permission'),
    path('display_and_edit/', views.display_and_edit, name='display_and_edit'),
    path('edit_workshop/single/<int:workshop_id>/', views.edit_single_workshop, name='edit_single_workshop'),
    path('edit_workshop/two_day/<int:workshop_id>/', views.edit_two_day_workshop, name='edit_two_day_workshop'),
    path('delete_workshop/<int:workshop_id>/', views.delete_workshop, name='delete_workshop'),
    path('add_workshop/', views.add_workshop, name='add_workshop'),
    path('get_students_by_class/<int:class_id>/', views.get_students_by_class, name='get_students_by_class'),
    path('update-student-permission/<int:student_id>/', views.update_student_permission, name='update_student_permission'),
    path('update-class-permission/<int:class_id>/', views.update_class_permission, name='update_class_permission'),
]
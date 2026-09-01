from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("register/", views.register, name="register"),
    path("students/", views.students, name="students"),
    path("students/add/", views.student_create, name="student_create"),
    path("students/<int:pk>/edit/", views.student_update, name="student_update"),
    path("students/<int:pk>/delete/", views.student_delete, name="student_delete"),
    path("students/<int:pk>/grades/", views.student_grades, name="student_grades"),
    path("courses/", views.courses, name="courses"),
    path("courses/add/", views.course_create, name="course_create"),
    path("courses/<int:pk>/edit/", views.course_update, name="course_update"),
    path("courses/<int:pk>/delete/", views.course_delete, name="course_delete"),
    path("enrolments/", views.enrolments, name="enrolments"),
    path("enrolments/add/", views.enrolment_create, name="enrolment_create"),
    path("enrolments/<int:pk>/edit/", views.enrolment_update, name="enrolment_update"),
    path("enrolments/<int:pk>/delete/", views.enrolment_delete, name="enrolment_delete"),
]

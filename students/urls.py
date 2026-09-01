from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("students/", views.students, name="students"),
    path("students/add/", views.student_create, name="student_create"),
    path("courses/", views.courses, name="courses"),
    path("courses/add/", views.course_create, name="course_create"),
    path("enrolments/", views.enrolments, name="enrolments"),
    path("enrolments/add/", views.enrolment_create, name="enrolment_create"),
]

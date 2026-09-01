from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from .forms import StudentForm, CourseForm, EnrolmentForm
from .models import Student, Course, Enrolment


def dashboard(request):
    return render(request, "students/dashboard.html", {
        "students_count": Student.objects.count(),
        "courses_count": Course.objects.count(),
        "enrolments_count": Enrolment.objects.count(),
    })


def students(request):
    return render(request, "students/students.html", {"students": Student.objects.order_by("last_name", "first_name")})


def student_create(request):
    form = StudentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Étudiant ajouté avec succès.")
        return redirect("students")
    return render(request, "students/form.html", {"form": form, "title": "Ajouter un étudiant"})


def courses(request):
    return render(request, "students/courses.html", {"courses": Course.objects.order_by("name")})


def course_create(request):
    form = CourseForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Cours ajouté avec succès.")
        return redirect("courses")
    return render(request, "students/form.html", {"form": form, "title": "Ajouter un cours"})


def enrolments(request):
    return render(request, "students/enrolments.html", {"enrolments": Enrolment.objects.select_related("student", "course")})


def enrolment_create(request):
    form = EnrolmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Inscription créée avec succès.")
        return redirect("enrolments")
    return render(request, "students/form.html", {"form": form, "title": "Nouvelle inscription"})

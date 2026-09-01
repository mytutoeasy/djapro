from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
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
    q = request.GET.get("q", "").strip()
    queryset = Student.objects.all().order_by("last_name", "first_name")
    if q:
        queryset = queryset.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q) | Q(phone__icontains=q))
    page_obj = Paginator(queryset, 10).get_page(request.GET.get("page"))
    return render(request, "students/students.html", {"page_obj": page_obj, "q": q})


def student_create(request):
    form = StudentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save(); messages.success(request, "Étudiant ajouté avec succès."); return redirect("students")
    return render(request, "students/form.html", {"form": form, "title": "Ajouter un étudiant"})


def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    form = StudentForm(request.POST or None, instance=student)
    if request.method == "POST" and form.is_valid():
        form.save(); messages.success(request, "Étudiant modifié avec succès."); return redirect("students")
    return render(request, "students/form.html", {"form": form, "title": "Modifier l'étudiant"})


def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        student.delete(); messages.success(request, "Étudiant supprimé avec succès."); return redirect("students")
    return render(request, "students/delete.html", {"object": student, "title": "Supprimer l'étudiant", "back_url": "students"})


def courses(request):
    q = request.GET.get("q", "").strip()
    queryset = Course.objects.all().order_by("name")
    if q:
        queryset = queryset.filter(Q(name__icontains=q) | Q(code__icontains=q) | Q(description__icontains=q))
    page_obj = Paginator(queryset, 10).get_page(request.GET.get("page"))
    return render(request, "students/courses.html", {"page_obj": page_obj, "q": q})


def course_create(request):
    form = CourseForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save(); messages.success(request, "Cours ajouté avec succès."); return redirect("courses")
    return render(request, "students/form.html", {"form": form, "title": "Ajouter un cours"})


def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    form = CourseForm(request.POST or None, instance=course)
    if request.method == "POST" and form.is_valid():
        form.save(); messages.success(request, "Cours modifié avec succès."); return redirect("courses")
    return render(request, "students/form.html", {"form": form, "title": "Modifier le cours"})


def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        course.delete(); messages.success(request, "Cours supprimé avec succès."); return redirect("courses")
    return render(request, "students/delete.html", {"object": course, "title": "Supprimer le cours", "back_url": "courses"})


def enrolments(request):
    q = request.GET.get("q", "").strip()
    queryset = Enrolment.objects.select_related("student", "course").order_by("-enrolment_date", "-id")
    if q:
        queryset = queryset.filter(Q(student__first_name__icontains=q) | Q(student__last_name__icontains=q) | Q(course__name__icontains=q) | Q(course__code__icontains=q) | Q(status__icontains=q))
    page_obj = Paginator(queryset, 10).get_page(request.GET.get("page"))
    return render(request, "students/enrolments.html", {"page_obj": page_obj, "q": q})


def enrolment_create(request):
    form = EnrolmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save(); messages.success(request, "Inscription créée avec succès."); return redirect("enrolments")
    return render(request, "students/form.html", {"form": form, "title": "Nouvelle inscription"})


def enrolment_update(request, pk):
    enrolment = get_object_or_404(Enrolment, pk=pk)
    form = EnrolmentForm(request.POST or None, instance=enrolment)
    if request.method == "POST" and form.is_valid():
        form.save(); messages.success(request, "Inscription modifiée avec succès."); return redirect("enrolments")
    return render(request, "students/form.html", {"form": form, "title": "Modifier l'inscription"})


def enrolment_delete(request, pk):
    enrolment = get_object_or_404(Enrolment, pk=pk)
    if request.method == "POST":
        enrolment.delete(); messages.success(request, "Inscription supprimée avec succès."); return redirect("enrolments")
    return render(request, "students/delete.html", {"object": enrolment, "title": "Supprimer l'inscription", "back_url": "enrolments"})

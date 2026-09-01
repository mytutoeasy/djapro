from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import StudentForm
from .models import Student


def student_list(request):
    students = Student.objects.all()
    return render(request, "students/list.html", {"students": students})


def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, "students/detail.html", {"student": student})


def student_create(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Étudiant ajouté avec succès.")
            return redirect("student_list")
    else:
        form = StudentForm()

    return render(request, "students/form.html", {"form": form, "title": "Ajouter un étudiant"})


def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Étudiant modifié avec succès.")
            return redirect("student_list")
    else:
        form = StudentForm(instance=student)

    return render(request, "students/form.html", {"form": form, "title": "Modifier l'étudiant"})


def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == "POST":
        student.delete()
        messages.success(request, "Étudiant supprimé avec succès.")
        return redirect("student_list")

    return render(request, "students/delete.html", {"student": student})

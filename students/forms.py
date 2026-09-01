from django import forms
from django.core.exceptions import ValidationError
from .models import Student, Course, Enrolment


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["first_name", "last_name", "email", "phone", "date_of_birth", "address"]
        widgets = {"date_of_birth": forms.DateInput(attrs={"type": "date"})}

    def clean_first_name(self):
        value = self.cleaned_data["first_name"].strip()
        if len(value) < 2 or not value.replace("-", "").isalpha():
            raise ValidationError("Le prénom doit contenir au moins 2 lettres.")
        return value.title()

    def clean_last_name(self):
        value = self.cleaned_data["last_name"].strip()
        if len(value) < 2 or not value.replace("-", "").isalpha():
            raise ValidationError("Le nom doit contenir au moins 2 lettres.")
        return value.title()

    def clean_phone(self):
        value = self.cleaned_data["phone"].strip()
        if value and not all(c.isdigit() or c in "+ -()" for c in value):
            raise ValidationError("Numéro de téléphone invalide.")
        return value


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["name", "code", "description", "duration", "price", "start_date", "end_date", "capacity", "status"]
        widgets = {"start_date": forms.DateInput(attrs={"type": "date"}), "end_date": forms.DateInput(attrs={"type": "date"})}

    def clean_code(self):
        return self.cleaned_data["code"].strip().upper()

    def clean_name(self):
        value = self.cleaned_data["name"].strip()
        if len(value) < 3:
            raise ValidationError("Le nom du cours doit contenir au moins 3 caractères.")
        return value

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get("start_date"), cleaned.get("end_date")
        if start and end and end < start:
            self.add_error("end_date", "La date de fin doit être après la date de début.")
        return cleaned


class EnrolmentForm(forms.ModelForm):
    class Meta:
        model = Enrolment
        fields = ["student", "course", "status", "grade", "attendance", "notes"]

    def clean(self):
        cleaned = super().clean()
        student, course = cleaned.get("student"), cleaned.get("course")
        if student and course:
            qs = Enrolment.objects.filter(student=student, course=course)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("Cet étudiant est déjà inscrit à ce cours.")
            if course.status != "active":
                raise ValidationError("Impossible de choisir un cours inactif.")
            if cleaned.get("status") in ["pending", "active"]:
                count = Enrolment.objects.filter(course=course, status__in=["pending", "active"]).exclude(pk=self.instance.pk).count()
                if count >= course.capacity:
                    raise ValidationError("La capacité maximale du cours est atteinte.")
        return cleaned

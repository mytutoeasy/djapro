from django import forms
from .models import Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "birth_date",
            "gender",
            "address",
        ]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
        }

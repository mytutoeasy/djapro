from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import StudentForm, CourseForm, EnrolmentForm
from .models import Student, Course, Enrolment

User = get_user_model()


class StudentModelTests(TestCase):
    def test_student_string(self):
        student = Student.objects.create(first_name="Ali", last_name="Amrani", email="ali@example.com")
        self.assertEqual(str(student), "Ali Amrani")

    def test_student_email_must_be_unique(self):
        Student.objects.create(first_name="Ali", last_name="Amrani", email="ali@example.com")
        form = StudentForm(data={"first_name": "Sara", "last_name": "Alaoui", "email": "ali@example.com"})
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class StudentFormTests(TestCase):
    def valid_data(self):
        return {"first_name": "Ahmed", "last_name": "Benali", "email": "ahmed@example.com", "phone": "+212 600000000", "date_of_birth": "2000-01-15", "address": "Rabat"}

    def test_invalid_first_name(self):
        data = self.valid_data()
        data["first_name"] = "A1"
        self.assertFalse(StudentForm(data=data).is_valid())

    def test_invalid_phone(self):
        data = self.valid_data()
        data["phone"] = "ABC123"
        self.assertFalse(StudentForm(data=data).is_valid())


class CourseFormTests(TestCase):
    def valid_data(self):
        return {"name": "Django Web", "code": "dj101", "description": "Course", "duration": 30, "price": "1500.00", "start_date": "2026-09-01", "end_date": "2026-10-01", "capacity": 20, "status": "active"}

    def test_code_is_normalized(self):
        form = CourseForm(data=self.valid_data())
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["code"], "DJ101")

    def test_end_date_before_start_date(self):
        data = self.valid_data()
        data["end_date"] = "2026-08-01"
        form = CourseForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("end_date", form.errors)

    def test_zero_duration_is_invalid(self):
        data = self.valid_data()
        data["duration"] = 0
        self.assertFalse(CourseForm(data=data).is_valid())

    def test_negative_price_is_invalid(self):
        data = self.valid_data()
        data["price"] = "-10"
        self.assertFalse(CourseForm(data=data).is_valid())

    def test_zero_capacity_is_invalid(self):
        data = self.valid_data()
        data["capacity"] = 0
        self.assertFalse(CourseForm(data=data).is_valid())


class EnrolmentFormTests(TestCase):
    def setUp(self):
        self.student = Student.objects.create(first_name="Ali", last_name="Amrani", email="ali@example.com")
        self.course = Course.objects.create(name="Django", code="DJ101", duration=30, price=Decimal("1000.00"), start_date=date.today(), end_date=date.today() + timedelta(days=30), capacity=2, status="active")

    def form_data(self, **overrides):
        data = {"student": self.student.pk, "course": self.course.pk, "status": "active", "grade": "80", "attendance": "90", "notes": "Good"}
        data.update(overrides)
        return data

    def test_duplicate_enrolment_is_invalid(self):
        Enrolment.objects.create(student=self.student, course=self.course, status="active")
        self.assertFalse(EnrolmentForm(data=self.form_data()).is_valid())

    def test_inactive_course_is_invalid(self):
        self.course.status = "inactive"
        self.course.save()
        self.assertFalse(EnrolmentForm(data=self.form_data()).is_valid())

    def test_capacity_is_enforced(self):
        student2 = Student.objects.create(first_name="Sara", last_name="Alaoui", email="sara@example.com")
        Enrolment.objects.create(student=self.student, course=self.course, status="active")
        Enrolment.objects.create(student=student2, course=self.course, status="active")
        student3 = Student.objects.create(first_name="Omar", last_name="Naji", email="omar@example.com")
        data = self.form_data(student=student3.pk)
        self.assertFalse(EnrolmentForm(data=data).is_valid())

    def test_grade_above_100_is_invalid(self):
        self.assertFalse(EnrolmentForm(data=self.form_data(grade="101")).is_valid())

    def test_attendance_above_100_is_invalid(self):
        self.assertFalse(EnrolmentForm(data=self.form_data(attendance="101")).is_valid())


class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="StrongPass123!")
        self.staff = User.objects.create_user(username="admin", password="StrongPass123!", is_staff=True)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

    def test_register_creates_and_logs_in_user(self):
        response = self.client.post(reverse("register"), {"username": "newuser", "password1": "StrongPass123!", "password2": "StrongPass123!"})
        self.assertRedirects(response, reverse("dashboard"))
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertFalse(response.wsgi_request.user.is_staff)

    def test_login_success(self):
        response = self.client.post(reverse("login"), {"username": "user", "password": "StrongPass123!"})
        self.assertRedirects(response, reverse("dashboard"))

    def test_login_failure(self):
        response = self.client.post(reverse("login"), {"username": "user", "password": "wrong"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct username and password")

    def test_logout(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"))

    def test_regular_user_can_view_students(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("students")).status_code, 200)

    def test_regular_user_cannot_create_student(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("student_create")).status_code, 302)

    def test_staff_can_create_student(self):
        self.client.force_login(self.staff)
        response = self.client.post(reverse("student_create"), {"first_name": "Sara", "last_name": "Alaoui", "email": "sara@example.com", "phone": "", "date_of_birth": "", "address": ""})
        self.assertRedirects(response, reverse("students"))
        self.assertTrue(Student.objects.filter(email="sara@example.com").exists())

    def test_regular_user_cannot_delete_student(self):
        student = Student.objects.create(first_name="Ali", last_name="Amrani", email="ali@example.com")
        self.client.force_login(self.user)
        response = self.client.get(reverse("student_delete", args=[student.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Student.objects.filter(pk=student.pk).exists())


class CRUDViewTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="admin", password="StrongPass123!", is_staff=True)
        self.client.force_login(self.staff)
        self.student = Student.objects.create(first_name="Ali", last_name="Amrani", email="ali@example.com")
        self.course = Course.objects.create(name="Django", code="DJ101", duration=30, price=Decimal("1000.00"), start_date=date.today(), end_date=date.today() + timedelta(days=30), capacity=20, status="active")
        self.enrolment = Enrolment.objects.create(student=self.student, course=self.course, status="active")

    def test_students_list_is_paginated(self):
        for i in range(12):
            Student.objects.create(first_name="Student", last_name=f"Test{i}", email=f"student{i}@example.com")
        response = self.client.get(reverse("students"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_student_search(self):
        response = self.client.get(reverse("students"), {"q": "Ali"})
        self.assertContains(response, "Ali Amrani")

    def test_course_search(self):
        response = self.client.get(reverse("courses"), {"q": "DJ101"})
        self.assertContains(response, "DJ101")

    def test_enrolment_search(self):
        response = self.client.get(reverse("enrolments"), {"q": "Ali"})
        self.assertContains(response, "Ali Amrani")

    def test_student_update(self):
        response = self.client.post(reverse("student_update", args=[self.student.pk]), {"first_name": "Omar", "last_name": "Amrani", "email": "ali@example.com", "phone": "", "date_of_birth": "", "address": ""})
        self.assertRedirects(response, reverse("students"))
        self.student.refresh_from_db()
        self.assertEqual(self.student.first_name, "Omar")

    def test_course_update(self):
        response = self.client.post(reverse("course_update", args=[self.course.pk]), {"name": "Django Advanced", "code": "DJ101", "description": "", "duration": 40, "price": "1200", "start_date": date.today().isoformat(), "end_date": (date.today() + timedelta(days=40)).isoformat(), "capacity": 25, "status": "active"})
        self.assertRedirects(response, reverse("courses"))

    def test_enrolment_update(self):
        response = self.client.post(reverse("enrolment_update", args=[self.enrolment.pk]), {"student": self.student.pk, "course": self.course.pk, "status": "completed", "grade": "95", "attendance": "98", "notes": "Excellent"})
        self.assertRedirects(response, reverse("enrolments"))

    def test_student_delete_requires_post(self):
        response = self.client.get(reverse("student_delete", args=[self.student.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Student.objects.filter(pk=self.student.pk).exists())

    def test_student_delete(self):
        response = self.client.post(reverse("student_delete", args=[self.student.pk]))
        self.assertRedirects(response, reverse("students"))
        self.assertFalse(Student.objects.filter(pk=self.student.pk).exists())

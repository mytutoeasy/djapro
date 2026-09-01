from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .dashboard_stats import dashboard_stats
from .forms import StudentForm, CourseForm, EnrolmentForm
from .models import Student, Course, Enrolment
User = get_user_model()

class StudentModelTests(TestCase):
    def test_student_string(self):
        student = Student.objects.create(first_name="Ali", last_name="Amrani", email="ali@example.com")
        self.assertEqual(str(student), "Ali Amrani")
    def test_student_email_must_be_unique(self):
        Student.objects.create(first_name="Ali", last_name="Amrani", email="ali@example.com")
        form = StudentForm(data={"first_name":"Sara","last_name":"Alaoui","email":"ali@example.com"})
        self.assertFalse(form.is_valid()); self.assertIn("email", form.errors)

class StudentFormTests(TestCase):
    def valid_data(self):
        return {"first_name":"Ahmed","last_name":"Benali","email":"ahmed@example.com","phone":"+212 600000000","date_of_birth":"2000-01-15","address":"Rabat"}
    def test_invalid_first_name(self):
        d=self.valid_data(); d["first_name"]="A1"; self.assertFalse(StudentForm(data=d).is_valid())
    def test_invalid_phone(self):
        d=self.valid_data(); d["phone"]="ABC123"; self.assertFalse(StudentForm(data=d).is_valid())

class CourseFormTests(TestCase):
    def valid_data(self):
        return {"name":"Django Web","code":"dj101","description":"Course","duration":30,"price":"1500.00","start_date":"2026-09-01","end_date":"2026-10-01","capacity":20,"status":"active"}
    def test_code_is_normalized(self):
        f=CourseForm(data=self.valid_data()); self.assertTrue(f.is_valid()); self.assertEqual(f.cleaned_data["code"],"DJ101")
    def test_end_date_before_start_date(self):
        d=self.valid_data(); d["end_date"]="2026-08-01"; f=CourseForm(data=d); self.assertFalse(f.is_valid()); self.assertIn("end_date",f.errors)
    def test_zero_duration_is_invalid(self):
        d=self.valid_data(); d["duration"]=0; self.assertFalse(CourseForm(data=d).is_valid())
    def test_negative_price_is_invalid(self):
        d=self.valid_data(); d["price"]="-10"; self.assertFalse(CourseForm(data=d).is_valid())
    def test_zero_capacity_is_invalid(self):
        d=self.valid_data(); d["capacity"]=0; self.assertFalse(CourseForm(data=d).is_valid())

class EnrolmentFormTests(TestCase):
    def setUp(self):
        self.student=Student.objects.create(first_name="Ali",last_name="Amrani",email="ali@example.com")
        self.course=Course.objects.create(name="Django",code="DJ101",duration=30,price=Decimal("1000.00"),start_date=date.today(),end_date=date.today()+timedelta(days=30),capacity=2,status="active")
    def form_data(self,**overrides):
        d={"student":self.student.pk,"course":self.course.pk,"status":"active","grade":"80","attendance":"90","notes":"Good"}; d.update(overrides); return d
    def test_duplicate_enrolment_is_invalid(self):
        Enrolment.objects.create(student=self.student,course=self.course,status="active"); self.assertFalse(EnrolmentForm(data=self.form_data()).is_valid())
    def test_inactive_course_is_invalid(self):
        self.course.status="inactive"; self.course.save(); self.assertFalse(EnrolmentForm(data=self.form_data()).is_valid())
    def test_capacity_is_enforced(self):
        s2=Student.objects.create(first_name="Sara",last_name="Alaoui",email="sara@example.com"); Enrolment.objects.create(student=self.student,course=self.course,status="active"); Enrolment.objects.create(student=s2,course=self.course,status="active"); s3=Student.objects.create(first_name="Omar",last_name="Naji",email="omar@example.com"); self.assertFalse(EnrolmentForm(data=self.form_data(student=s3.pk)).is_valid())
    def test_grade_above_100_is_invalid(self): self.assertFalse(EnrolmentForm(data=self.form_data(grade="101")).is_valid())
    def test_attendance_above_100_is_invalid(self): self.assertFalse(EnrolmentForm(data=self.form_data(attendance="101")).is_valid())

class DashboardTests(TestCase):
    def setUp(self):
        self.user=User.objects.create_user(username="admin",password="StrongPass123!",is_staff=True); self.client.force_login(self.user)
        self.s1=Student.objects.create(first_name="Ali",last_name="Amrani",email="ali@example.com"); self.s2=Student.objects.create(first_name="Sara",last_name="Alaoui",email="sara@example.com")
        self.c1=Course.objects.create(name="Django",code="DJ101",duration=30,price=Decimal("1000"),start_date=date.today(),end_date=date.today()+timedelta(days=30),capacity=10,status="active")
        self.c2=Course.objects.create(name="Python",code="PY101",duration=20,price=Decimal("800"),start_date=date.today(),end_date=date.today()+timedelta(days=20),capacity=5,status="active")
        Enrolment.objects.create(student=self.s1,course=self.c1,status="completed",grade=80); Enrolment.objects.create(student=self.s2,course=self.c1,status="active",grade=60); Enrolment.objects.create(student=self.s1,course=self.c2,status="pending")
    def test_dashboard_counts(self):
        stats=dashboard_stats(); self.assertEqual(stats["students_count"],2); self.assertEqual(stats["courses_count"],2); self.assertEqual(stats["enrolments_count"],3); self.assertEqual(stats["active_enrolments_count"],1); self.assertEqual(stats["completed_enrolments_count"],1); self.assertEqual(stats["pending_enrolments_count"],1)
    def test_dashboard_average_grade(self): self.assertEqual(dashboard_stats()["average_grade"],Decimal("70"))
    def test_students_per_course_and_remaining_places(self):
        courses={c.code:c for c in dashboard_stats()["students_per_course"]}; self.assertEqual(courses["DJ101"].student_count,2); self.assertEqual(courses["DJ101"].remaining_places,8); self.assertEqual(courses["PY101"].student_count,1); self.assertEqual(courses["PY101"].remaining_places,4)
    def test_dashboard_page(self): self.assertEqual(self.client.get(reverse("dashboard")).status_code,200)

class GradeTests(TestCase):
    def setUp(self):
        self.student=Student.objects.create(first_name="Ali",last_name="Amrani",email="ali@example.com"); self.course=Course.objects.create(name="Django",code="DJ101",duration=30,price=Decimal("1000"),start_date=date.today(),end_date=date.today()+timedelta(days=30),capacity=10,status="active")
    def test_passed_at_50(self): self.assertTrue(Enrolment(student=self.student,course=self.course,grade=50).passed)
    def test_failed_below_50(self): self.assertFalse(Enrolment(student=self.student,course=self.course,grade=49).passed)
    def test_no_grade_is_not_passed(self): self.assertFalse(Enrolment(student=self.student,course=self.course).passed)

class AuthenticationTests(TestCase):
    def setUp(self): self.user=User.objects.create_user(username="user",password="StrongPass123!"); self.staff=User.objects.create_user(username="admin",password="StrongPass123!",is_staff=True)
    def test_anonymous_dashboard_redirect(self): self.assertRedirects(self.client.get(reverse("dashboard")),f"{reverse('login')}?next={reverse('dashboard')}")
    def test_register(self):
        r=self.client.post(reverse("register"),{"username":"newuser","password1":"StrongPass123!","password2":"StrongPass123!"}); self.assertRedirects(r,reverse("dashboard")); self.assertTrue(r.wsgi_request.user.is_authenticated); self.assertFalse(r.wsgi_request.user.is_staff)
    def test_login_success(self): self.assertRedirects(self.client.post(reverse("login"),{"username":"user","password":"StrongPass123!"}),reverse("dashboard"))
    def test_login_failure(self): self.assertEqual(self.client.post(reverse("login"),{"username":"user","password":"wrong"}).status_code,200)
    def test_logout(self): self.client.force_login(self.user); self.assertRedirects(self.client.post(reverse("logout")),reverse("login"))
    def test_regular_user_can_view_students(self): self.client.force_login(self.user); self.assertEqual(self.client.get(reverse("students")).status_code,200)
    def test_regular_user_cannot_create_student(self): self.client.force_login(self.user); self.assertEqual(self.client.get(reverse("student_create")).status_code,302)
    def test_staff_can_access_create_pages(self): self.client.force_login(self.staff); self.assertEqual(self.client.get(reverse("student_create")).status_code,200); self.assertEqual(self.client.get(reverse("course_create")).status_code,200); self.assertEqual(self.client.get(reverse("enrolment_create")).status_code,200)

class GradeViewTests(TestCase):
    def setUp(self):
        self.user=User.objects.create_user(username="user",password="StrongPass123!"); self.client.force_login(self.user); self.student=Student.objects.create(first_name="Ali",last_name="Amrani",email="ali@example.com"); self.course=Course.objects.create(name="Django",code="DJ101",duration=30,price=Decimal("1000"),start_date=date.today(),end_date=date.today()+timedelta(days=30),capacity=10,status="active"); Enrolment.objects.create(student=self.student,course=self.course,status="completed",grade=85,attendance=95)
    def test_grade_history_page(self):
        r=self.client.get(reverse("student_grades",args=[self.student.pk])); self.assertEqual(r.status_code,200); self.assertContains(r,"85.00"); self.assertEqual(r.context["average_grade"],Decimal("85"))

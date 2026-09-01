from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError


class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Course(models.Model):
    STATUS_CHOICES = [("active", "Active"), ("inactive", "Inactive")]
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True)
    duration = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10000)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    start_date = models.DateField()
    end_date = models.DateField()
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10000)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError({"end_date": "La date de fin doit être après la date de début."})

    def __str__(self):
        return f"{self.code} - {self.name}"


class Enrolment(models.Model):
    STATUS_CHOICES = [("pending", "Pending"), ("active", "Active"), ("completed", "Completed"), ("cancelled", "Cancelled")]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrolments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrolments")
    enrolment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    attendance = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["student", "course"], name="unique_student_course")]

    def clean(self):
        if self.course_id and self.course.status != "active":
            raise ValidationError("Impossible de s'inscrire à un cours inactif.")
        if self.course_id and self.pk is None:
            current = Enrolment.objects.filter(course=self.course, status__in=["pending", "active"]).count()
            if current >= self.course.capacity:
                raise ValidationError("La capacité maximale du cours est atteinte.")

    @property
    def passed(self):
        return self.grade is not None and self.grade >= 50

    def __str__(self):
        return f"{self.student} → {self.course}"

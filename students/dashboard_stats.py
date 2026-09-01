from django.db.models import Avg, Count, F, IntegerField, ExpressionWrapper
from .models import Student, Course, Enrolment


def dashboard_stats():
    students_per_course = Course.objects.annotate(
        student_count=Count("enrolments", distinct=True),
    ).annotate(
        remaining_places=ExpressionWrapper(
            F("capacity") - F("student_count"), output_field=IntegerField()
        )
    ).order_by("name")

    return {
        "students_count": Student.objects.count(),
        "courses_count": Course.objects.count(),
        "enrolments_count": Enrolment.objects.count(),
        "active_enrolments_count": Enrolment.objects.filter(status="active").count(),
        "completed_enrolments_count": Enrolment.objects.filter(status="completed").count(),
        "pending_enrolments_count": Enrolment.objects.filter(status="pending").count(),
        "cancelled_enrolments_count": Enrolment.objects.filter(status="cancelled").count(),
        "average_grade": Enrolment.objects.filter(grade__isnull=False).aggregate(avg=Avg("grade"))["avg"],
        "students_per_course": students_per_course,
        "enrolments_by_status": Enrolment.objects.values("status").annotate(total=Count("id")).order_by("status"),
    }

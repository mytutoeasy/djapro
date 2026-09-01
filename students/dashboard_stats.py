from django.db.models import Count, Avg
from .models import Student, Course, Enrolment


def dashboard_stats():
    return {
        "students_count": Student.objects.count(),
        "courses_count": Course.objects.count(),
        "enrolments_count": Enrolment.objects.count(),
        "active_enrolments_count": Enrolment.objects.filter(status="active").count(),
        "completed_enrolments_count": Enrolment.objects.filter(status="completed").count(),
        "pending_enrolments_count": Enrolment.objects.filter(status="pending").count(),
        "cancelled_enrolments_count": Enrolment.objects.filter(status="cancelled").count(),
        "average_grade": Enrolment.objects.filter(grade__isnull=False).aggregate(avg=Avg("grade"))["avg"],
        "students_per_course": Course.objects.annotate(student_count=Count("enrolments", distinct=True)).order_by("name"),
        "enrolments_by_status": Enrolment.objects.values("status").annotate(total=Count("id")).order_by("status"),
    }

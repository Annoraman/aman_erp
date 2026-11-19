# apps/hr/services/attendance_service.py

from django.db.models import Count


class AttendanceService:

    @staticmethod
    def summarize(employee, start, end):

        if not employee:
            return AttendanceService._empty_result()

        records = employee.attendance_set.filter(
            date__range=(start, end)
        )

        total_days = records.count()

        absent_days = records.filter(is_absent=True).count()
        late_days = records.filter(is_late=True).count()
        #present_days = records.filter(1=1).count()
        #leave_days = records.filter(1=1).count()

        total_hours = records.aggregate(
            total=Count("worked_hours")
        )["total"] or 0

        return {
            "total_days": total_days,
            #"present_days": present_days,
            "absent_days": absent_days,
            #"leave_days": leave_days,
            "late_days": late_days,
            "total_hours": total_hours,
        }

    # --------------------------
    # SAFE EMPTY STATE
    # --------------------------
    @staticmethod
    def _empty_result():
        return {
            "total_days": 0,
            "present_days": 0,
            "absent_days": 0,
            "leave_days": 0,
            "late_days": 0,
            "total_hours": 0,
        }
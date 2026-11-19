# apps/hr/selectors/attendance_selectors.py

from apps.hr.models import Attendance


class AttendanceSelector:

    @staticmethod
    def get_employee_attendance(employee, start, end):
        return Attendance.objects.filter(
            employee=employee,
            date__range=(start, end)
        )
# apps/hr/selectors/leave_selectors.py

from apps.hr.models import LeaveRequest


class LeaveSelector:

    @staticmethod
    def get_approved_leaves(employee, start, end):
        return LeaveRequest.objects.filter(
            employee=employee,
            status="APPROVED",
            start_date__lte=end,
            end_date__gte=start
        )
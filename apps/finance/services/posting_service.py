# apps/finance/services/posting_service.py

from django.core.exceptions import PermissionDenied

from apps.accounts.services.permission_service import PermissionService
from apps.finance.models import JournalEntry
from apps.finance.services.audit_service import AuditService



class PostingService:

    @staticmethod
    def post_journal(user, journal: JournalEntry):

        # 🔐 RBAC check
        if not PermissionService.has_permission(user, "finance.post_journal"):
            raise PermissionDenied("User cannot post journals")

        # 🚫 Already posted
        if journal.is_posted:
            raise ValueError("Journal already posted")

        # 🚫 Prevent posting in closed period (Step 7.6)
        if journal.fiscal_period.is_closed:
            raise ValueError("Cannot post journal in a closed period")

        lines = journal.lines.all()

        # 🚫 Must have at least 2 lines (basic accounting rule)
        if lines.count() < 2:
            raise ValueError("Journal must have at least two lines")

        # ⚖️ Ensure balance
        total_debit = sum(l.debit for l in lines)
        total_credit = sum(l.credit for l in lines)

        if total_debit != total_credit:
            raise ValueError("Cannot post unbalanced journal")

        # 🔒 Optional: ensure all accounts belong to same company
        for line in lines:
            if line.account.company_id != journal.company_id:
                raise ValueError("Account company mismatch in journal lines")

            # 🔒 Optional: cost center validation
            if line.cost_center and line.cost_center.company_id != journal.company_id:
                raise ValueError("Cost center company mismatch")

        # ✅ Mark as posted
        journal.is_posted = True
        journal.save(update_fields=["is_posted"])

        AuditService.log(
            user,
            "POST",
            journal,
            description="Journal posted"
        )

        return journal

from django.contrib.auth import get_user_model


#finance/services/journal_service.py
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import PermissionDenied, ValidationError
from apps.finance.models import JournalEntry, JournalLine
from apps.finance.services.period_service import PeriodService
from apps.accounts.services.permission_service import PermissionService


class JournalService:

    @staticmethod
    @transaction.atomic
    def create_journal(user, data):

        # 🔐 RBAC
        if not PermissionService.has_permission(user, "finance.create_journal"):
            raise PermissionDenied("User cannot create journal entries")

        # ✅ Secure company source
        company = user.company

        # 📅 Resolve fiscal period
        period = PeriodService.get_period(company, data["date"])

        # 🚫 Closed period
        if period.is_closed:
            raise ValidationError("Cannot create journal in a closed period")

        # 🧾 Create Journal Entry
        journal = JournalEntry.objects.create(
            date=data["date"],
            description=data["description"],
            reference=data.get("reference"),
            company=company,
            fiscal_period=period,
        )

        total_debit = Decimal("0.00")
        total_credit = Decimal("0.00")

        # 🧮 Calculate totals
        for line_data in data["lines"]:
            debit = Decimal(line_data.get("debit", 0) or 0)
            credit = Decimal(line_data.get("credit", 0) or 0)

            total_debit += debit
            total_credit += credit

        # ⚖️ Validate balance
        if total_debit != total_credit:
            raise ValidationError(
                f"Unbalanced journal: Debit {total_debit} != Credit {total_credit}"
            )

        # ➕ Create Lines
        for line_data in data["lines"]:
            account = line_data["account"]
            cost_center = line_data.get("cost_center")

            # 🔒 Account validation
            if account.company_id != company.id:
                raise ValidationError("Account must belong to the same company")

            # 🔒 Cost center validation
            if cost_center and cost_center.company_id != company.id:
                raise ValidationError("Cost center must belong to the same company")

            debit = Decimal(line_data.get("debit", 0) or 0)
            credit = Decimal(line_data.get("credit", 0) or 0)

            JournalLine.objects.create(
                journal=journal,
                account=account,
                debit=debit,
                credit=credit,
                cost_center=cost_center,
            )

        return journal

    @staticmethod
    @transaction.atomic
    def post_journal(user, journal_id):

        # 🔐 Permission
        if not PermissionService.has_permission(user, "finance.post_journal"):
            raise PermissionDenied("User cannot post journal entries")

        # 🔒 Lock row (important for concurrency)
        journal = JournalEntry.objects.select_for_update().get(id=journal_id)

        # 🚫 Already posted
        if journal.is_posted:
            raise ValidationError("Journal already posted")

        # 🚫 Closed period
        if journal.fiscal_period.is_closed:
            raise ValidationError("Cannot post journal in a closed period")

        # 🚫 No lines
        if not journal.lines.exists():
            raise ValidationError("Cannot post journal without lines")

        # ⚖️ Final balance check (CRITICAL)
        total_debit = journal.total_debit()
        total_credit = journal.total_credit()

        if total_debit != total_credit:
            raise ValidationError(
                f"Unbalanced journal: Debit {total_debit} != Credit {total_credit}"
            )

        # ✅ Mark as posted
        journal.is_posted = True
        journal.save()

        return journal

    @staticmethod
    @transaction.atomic
    def reverse_journal(user, journal_id, reversal_date=None):

        # 🔐 Permission
        if not PermissionService.has_permission(user, "finance.reverse_journal"):
            raise PermissionDenied("User cannot reverse journal entries")

        # 🔒 Lock original journal
        original = JournalEntry.objects.select_for_update().get(id=journal_id)

        # 🚫 Must be posted
        if not original.is_posted:
            raise ValidationError("Only posted journals can be reversed")

        # 🚫 Already reversed
        if hasattr(original, "reversal_entry"):
            raise ValidationError("Journal already reversed")

        # 📅 Use same date if not provided
        reversal_date = reversal_date or original.date

        # 📅 Resolve period
        period = PeriodService.get_period(original.company, reversal_date)

        if period.is_closed:
            raise ValidationError("Cannot reverse in a closed period")

        # 🧾 Create reversal journal
        reversal = JournalEntry.objects.create(
            date=reversal_date,
            description=f"Reversal of JE-{original.id}",
            reference=original.reference,
            company=original.company,
            fiscal_period=period,
            is_reversal=True,
            reversed_entry=original
        )

        # 🔁 Reverse lines
        for line in original.lines.all():
            JournalLine.objects.create(
                journal=reversal,
                account=line.account,
                debit=line.credit,
                credit=line.debit,
                cost_center=line.cost_center
            )

        # ✅ Post reversal immediately
        reversal.is_posted = True
        reversal.save()

        return reversal
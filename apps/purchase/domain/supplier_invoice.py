from decimal import Decimal
from django.core.exceptions import ValidationError


class SupplierInvoice:

    def __init__(self, supplier, company, user):
        self.supplier = supplier
        self.company = company
        self.created_by = user

        self.lines = []
        self.total_amount = Decimal("0.00")

        self.status = "draft"
        self.journal_entry = None

    # =====================================================
    # ADD LINE (INVARIANT ENFORCEMENT HERE)
    # =====================================================
    def add_line(self, grn_line, quantity, unit_price):

        if quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")

        available_qty = grn_line.quantity - grn_line.invoiced_quantity

        if quantity > available_qty:
            raise ValidationError(
                f"Cannot invoice more than available. "
                f"Available={available_qty}, Requested={quantity}"
            )

        self.lines.append({
            "grn_line": grn_line,
            "quantity": quantity,
            "unit_price": unit_price,
            "amount": Decimal(quantity) * Decimal(str(unit_price))
        })

        self.total_amount += Decimal(quantity) * Decimal(str(unit_price))

    # =====================================================
    # BUSINESS RULE: STATUS CALCULATION
    # =====================================================
    def calculate_status(self, config):

        if not config or not config.grni_account:
            raise ValidationError("GRNI account not configured.")

        matched = all(
            line["quantity"] <= (line["grn_line"].quantity)
            for line in self.lines
        )

        return "fully_matched" if matched else "partially_matched"

    # =====================================================
    # BUSINESS RULE: ELIGIBILITY FOR POSTING
    # =====================================================
    def can_post(self):
        return self.status in ["fully_matched", "partially_matched"] \
            and self.journal_entry is None

    def mark_posted(self, journal_entry):
        if self.journal_entry:
            raise ValidationError("Already posted.")

        self.journal_entry = journal_entry
        self.status = "posted"
# apps/purchase/services/matching_service.py

from decimal import Decimal
from django.db.models import Sum


class MatchingEngine:
    """
    ERP 3-Way Matching Engine:

    PO ↔ GRN ↔ Invoice

    Responsible for:
    - Quantity matching
    - Value matching
    - Tolerance handling
    - Status decision
    """

    # =====================================================
    # MAIN ENTRY POINT
    # =====================================================
    @staticmethod
    def evaluate_invoice(invoice, config):
        """
        Returns:
            - fully_matched
            - partially_matched
            - over_billed
            - mismatch
        """

        invoice_total = Decimal("0.00")

        invoice_lines = invoice.lines.select_related(
            "grn_line",
            "grn_line__purchase_order_line"
        )

        all_fully_matched = True
        any_matched = False

        for line in invoice_lines:
            grn_line = line.grn_line
            po_line = grn_line.purchase_order_line

            # -------------------------
            # Quantity checks
            # -------------------------
            po_qty = po_line.quantity
            grn_qty = grn_line.quantity
            inv_qty = line.invoiced_quantity

            # -------------------------
            # Value calculation
            # -------------------------
            expected_value = po_qty * po_line.unit_price
            actual_value = inv_qty * line.unit_price

            invoice_total += actual_value

            # -------------------------
            # Tolerance logic
            # -------------------------
            qty_diff = abs(grn_qty - inv_qty)
            price_diff = abs(expected_value - actual_value)

            qty_tolerance = (config.quantity_tolerance_percent / 100) * po_qty
            price_tolerance = (config.price_tolerance_percent / 100) * expected_value

            line_fully_matched = (
                qty_diff <= qty_tolerance and
                price_diff <= price_tolerance
            )

            if line_fully_matched:
                any_matched = True
            else:
                all_fully_matched = False

        # =================================================
        # FINAL DECISION LOGIC
        # =================================================
        if all_fully_matched:
            return "fully_matched"

        if any_matched:
            return "partially_matched"

        return "mismatch"

    # =====================================================
    # PO LEVEL MATCH SUMMARY
    # =====================================================
    @staticmethod
    def evaluate_po(po):
        """
        Aggregates PO status from GRN + Invoice progress
        """

        lines = po.lines.all()

        total_ordered = Decimal("0.00")
        total_received = Decimal("0.00")
        total_invoiced = Decimal("0.00")

        for line in lines:
            total_ordered += line.quantity
            total_received += line.received_quantity
            total_invoiced += line.invoiced_quantity

        if total_received == 0:
            return "approved"

        if total_received < total_ordered:
            return "partially_received"

        if total_invoiced < total_received:
            return "received_not_invoiced"

        return "closed"
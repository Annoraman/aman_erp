# apps/finance/services/reconciliation_service.py

class ReconciliationService:

    @staticmethod
    def match_statement_line(statement_line, payment):

        if statement_line.is_matched:
            raise ValueError("Already matched")

        if payment.is_posted is False:
            raise ValueError("Payment not posted")

        if statement_line.amount != payment.amount:
            raise ValueError("Amount mismatch")

        statement_line.matched_payment = payment
        statement_line.is_matched = True
        statement_line.save()

        return statement_line
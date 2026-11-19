from apps.purchase.models.supplier_invoice import SupplierInvoice

class APSelector:

    @staticmethod
    def outstanding_invoices(company):
        return SupplierInvoice.objects.filter(
            company=company,
            status__in=["posted", "partially_paid"]
        )

    @staticmethod
    def supplier_balance(supplier):
        invoices = supplier.supplierinvoice_set.all()

        total = sum(i.total_amount for i in invoices)
        paid = sum(i.paid_amount for i in invoices)

        return total - paid
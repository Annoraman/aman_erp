from core import models


class APInvoiceBalance(models.Model):
    invoice = models.OneToOneField("purchases.SupplierInvoice", on_delete=models.CASCADE)
    vendor = models.ForeignKey("purchases.Vendor", on_delete=models.CASCADE)

    invoice_date = models.DateField()
    due_date = models.DateField()

    original_amount = models.DecimalField(max_digits=18, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    open_amount = models.DecimalField(max_digits=18, decimal_places=2)

    is_closed = models.BooleanField(default=False)
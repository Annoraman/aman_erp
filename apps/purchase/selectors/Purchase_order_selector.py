#apps\purchase\selectors\PurchaseOrderSelector.py
from apps.purchase.models.purchase_order import PurchaseOrder

class PurchaseOrderSelector:

    @staticmethod
    def list_by_company(company):
        return PurchaseOrder.objects.for_company(company).select_related("supplier")

    @staticmethod
    def list_by_company(company):
        return PurchaseOrder.objects.for_company(company).select_related("supplier")
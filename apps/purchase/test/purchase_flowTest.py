#purchase\test\purchase_flowTest.py
from unittest import TestCase
from apps.purchase.services.goods_receipt_service import GoodsReceiptService
from apps.purchase.services.purchase_order_service import PurchaseOrderService
from apps.purchase.services.supplier_invoice_service import SupplierInvoiceService


class PurchaseFlowTest(TestCase):

    def test_full_purchase_flow(self):
        po = PurchaseOrderService.create_po(...)

        grn = GoodsReceiptService.create_grn(...)

        invoice = SupplierInvoiceService.post_invoice(...)

        self.assertEqual(invoice.status, "posted")
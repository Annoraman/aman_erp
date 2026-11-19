from django.db import models                       # استيراد مكتبة النماذج من Django

class POStatus(models.TextChoices):                # حالات أمر الشراء (Purchase Order)

    # -------------------------
    # CREATION
    # -------------------------
    DRAFT = "draft", "Draft"             # أمر شراء في مرحلة الإنشاء ولم يتم اعتماده بعد
    APPROVED = "approved", "Approved"    # تم اعتماد أمر الشراء

    # -------------------------
    # COMMUNICATION
    # -------------------------
    SENT = "sent", "Sent"                # تم إرسال أمر الشراء إلى المورد

    # -------------------------
    # EXECUTION (Warehouse)
    # -------------------------
    PARTIALLY_RECEIVED = "partially_received", "Partially Received"  # تم استلام جزء من الكمية
    FULLY_RECEIVED = "fully_received", "Fully Received"              # تم استلام الكمية كاملة

    # -------------------------
    # FINANCIAL (AP)
    # -------------------------
    PARTIALLY_INVOICED = "partially_invoiced", "Partially Invoiced"  # تم إصدار فواتير لجزء من الكمية
    FULLY_INVOICED = "fully_invoiced", "Fully Invoiced"              # تم إصدار فواتير لكل الكمية

    # -------------------------
    # COMPLETION
    # -------------------------
    CLOSED = "closed", "Closed"                                     # تم إغلاق أمر الشراء (اكتمل الاستلام والفوترة)

    # -------------------------
    # EXCEPTION
    # -------------------------
    CANCELLED = "cancelled", "Cancelled"  # تم إلغاء أمر الشراء


class InvoiceStatus(models.TextChoices):  # حالات فاتورة المورد

    # -------------------------
    # CREATION
    # -------------------------
    DRAFT = "draft", "Draft"  # الفاتورة في حالة مسودة

    # -------------------------
    # MATCHING (GRN/PO)
    # -------------------------
    PARTIALLY_MATCHED = "partially_matched", "Partially Matched"  # الفاتورة مطابقة جزئيًا مع الاستلام/أمر الشراء
    FULLY_MATCHED = "fully_matched", "Fully Matched"  # الفاتورة مطابقة بالكامل

    # -------------------------
    # ACCOUNTING
    # -------------------------
    POSTED = "posted", "Posted"  # تم ترحيل الفاتورة إلى الحسابات (القيود المحاسبية)

    # -------------------------
    # PAYMENT
    # -------------------------
    PARTIALLY_PAID = "partially_paid", "Partially Paid"  # تم دفع جزء من الفاتورة
    PAID = "paid", "Paid"  # تم دفع الفاتورة بالكامل

    # -------------------------
    # EXCEPTIONS
    # -------------------------
    CANCELLED = "cancelled", "Cancelled"  # تم إلغاء الفاتورة
    REVERSED = "reversed", "Reversed"  # تم عكس القيد المحاسبي للفاتورة


class GRNStatus(models.TextChoices):  # حالات إذن الاستلام (Goods Receipt Note)

    # -------------------------
    # INITIAL
    # -------------------------
    DRAFT = "draft", "Draft"  # إذن الاستلام في حالة مسودة

    # -------------------------
    # OPERATIONAL FLOW
    # -------------------------
    CONFIRMED = "confirmed", "Confirmed"  # تم تأكيد إذن الاستلام
    PARTIALLY_RECEIVED = "partially_received", "Partially Received"  # تم استلام جزء من الكمية
    FULLY_RECEIVED = "fully_received", "Fully Received"  # تم استلام الكمية كاملة

    # -------------------------
    # INVOICING (AP Integration)
    # -------------------------
    NOT_INVOICED = "not_invoiced", "Not Invoiced"  # لم يتم إصدار أي فاتورة بعد
    PARTIALLY_INVOICED = "partially_invoiced", "Partially Invoiced"  # تم إصدار فواتير جزئية
    FULLY_INVOICED = "fully_invoiced", "Fully Invoiced"  # تم إصدار فواتير كاملة

    # -------------------------
    # FINANCIAL COMPLETION
    # -------------------------
    CLOSED = "closed", "Closed"                      # تم الإغلاق (استلام كامل + فوترة كاملة)

    # -------------------------
    # EXCEPTIONS
    # -------------------------
    CANCELLED = "cancelled", "Cancelled"             # تم إلغاء الإذن
    RETURNED = "returned", "Returned"                # تم إرجاع البضاعة للمورد

from django.db import models                     # استيراد مكتبة Django الخاصة بالنماذج


class StockMovementType(models.TextChoices):     # تعريف أنواع حركات المخزون

    # -------------------------
    # INBOUND (Stock Increase)
    # -------------------------
    PURCHASE_RECEIPT = "purchase_receipt", "Purchase Receipt"    # استلام بضاعة من المورد (زيادة المخزون)
    CUSTOMER_RETURN = "customer_return", "Customer Return"       # مرتجع من العميل (زيادة المخزون)
    ADJUSTMENT_IN = "adjustment_in", "Adjustment In"             # تسوية زيادة (تصحيح مخزون)
    TRANSFER_IN = "transfer_in", "Transfer In"                   # تحويل من مخزن آخر (زيادة المخزون)
    PRODUCTION_IN = "production_in", "Production Output"         # إنتاج مصنع (زيادة المخزون)

    # -------------------------
    # OUTBOUND (Stock Decrease)
    # -------------------------
    SALES_DELIVERY = "sales_delivery", "Sales Delivery"          # تسليم للعميل (نقص المخزون)
    SUPPLIER_RETURN = "supplier_return", "Supplier Return"       # إرجاع للمورد (نقص المخزون)
    ADJUSTMENT_OUT = "adjustment_out", "Adjustment Out"          # تسوية نقص (تصحيح مخزون)
    TRANSFER_OUT = "transfer_out", "Transfer Out"                # تحويل إلى مخزن آخر (نقص المخزون)
    PRODUCTION_OUT = "production_out", "Production Consumption"  # استهلاك في الإنتاج (نقص المخزون)

    # -------------------------
    # SYSTEM / CORRECTIONS
    # -------------------------
    INVENTORY_COUNT = "inventory_count", "Inventory Count"       # جرد فعلي للمخزون
    SCRAP = "scrap", "Scrap"                                     # إتلاف بضاعة (نقص المخزون)
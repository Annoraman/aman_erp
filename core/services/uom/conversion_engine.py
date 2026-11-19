from decimal import Decimal
from django.core.exceptions import ValidationError


class UOMConversionEngine:

    @staticmethod
    def convert(quantity, from_uom, to_uom):

        # same unit
        if from_uom == to_uom:
            return quantity

        # must be same category (ERP rule)
        if from_uom.category_id != to_uom.category_id:
            raise ValidationError("Cannot convert between different UOM categories")

        # convert to base
        base_qty = Decimal(quantity) * from_uom.ratio_to_base

        # convert from base to target
        result = base_qty / to_uom.ratio_to_base

        return result
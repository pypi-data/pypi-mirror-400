# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.tools import cached_property

from .edocument import Invoice


class InvoiceStock(Invoice):
    "EDocument Spanish Facturae Invoice - stock extension"
    __name__ = 'edocument.es.facturae.invoice'

    @cached_property
    def delivery_notes_references(self):
        shipments = {
            m.shipment for l in self.lines
            for m in l.stock_moves if m.shipment}
        return [(s.number, s.effective_date) for s in shipments]

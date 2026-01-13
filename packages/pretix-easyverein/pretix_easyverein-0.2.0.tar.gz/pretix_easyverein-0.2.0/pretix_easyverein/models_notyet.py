from typing import Any

from django.db import models
from easyverein import EasyvereinAPIException
from easyverein.models import (
    InvoiceCreate as EVInvoiceCreate,
    InvoiceUpdate as EVInvoiceUpdate,
)
from pretix.base.invoice import Invoice


class EasyvereinInvoiceSync(models.Model):
    invoice = models.ForeignKey(
        Invoice, related_name="ev_sync", on_delete=models.CASCADE
    )
    ev_invoice_id = models.IntegerField(null=True, default=None)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def upload2ev(self, ev_client):
        i = self.invoice
        tax_rate = [line.tax_rate for line in i.lines.all()]
        if tax_rate[1:] == tax_rate[:-1]:
            tax_rate = float(tax_rate[0])
        else:
            raise ValueError(f"Tax rate of entries in {i} differs.")

        ev_invoice_create = EVInvoiceCreate(
            kind="revenue" if not i.is_cancellation else "cancel",
            date=i.date,
            # dateItHappend="2024-11-20",  # TODO event date
            invNumber=i.number,
            refNumber=f"{i.event}-{i.order}",  # TODO event prefix
            receiver=i.address_invoice_to,
            totalPrice=float(sum([line.gross_value for line in i.lines.all()])),
            tax=float(sum([line.tax_value for line in i.lines.all()])),
            taxRate=tax_rate,
            gross=True,
        )
        ev_invoice_create.isDraft = True
        try:
            ev_invoice = ev_client.invoice.create(ev_invoice_create)
        except EasyvereinAPIException as e:
            print(e)
            raise
        ev_client.invoice.upload_attachment(ev_invoice, self.invoice.file)
        ev_invoice = ev_client.invoice.update(
            ev_invoice, EVInvoiceUpdate(isDraft=False)
        )
        self.ev_invoice_id = ev_invoice.id
        self.save(update_fields=["ev_invoice_id"])

    def link2ev(self, ev_invoice_id):
        self.ev_invoice_id = ev_invoice_id
        self.save(update_fields=["ev_invoice_id"])

from .client import http_delete as http_delete, http_get as http_get, http_patch as http_patch, http_post as http_post
from .model import MoneybirdModel as MoneybirdModel
from .payment import Payment as Payment
from pydantic import BaseModel
from typing import Any

class ExternalSalesInvoiceDetailsAttribute(BaseModel):
    id: int | None
    description: str | None
    period: str | None
    price: int | str | None
    amount: int | str | None
    tax_rate_id: int | None
    ledger_account_id: str | None
    project_id: str | None
    def update(self, data: dict[str, Any]) -> None: ...

class ExternalSalesInvoice(MoneybirdModel):
    contact_id: int | None
    reference: str | None
    date: str | None
    due_date: str | None
    currency: str | None
    prices_are_incl_tax: bool | None
    source: str | None
    source_url: str | None
    details: list[ExternalSalesInvoiceDetailsAttribute] | None
    payments: list[Payment] | None
    def ensure_payments(cls, value: list[dict[str, Any]] | list[Payment] | None) -> list[Payment] | None: ...
    def update(self, data: dict[str, Any]) -> None: ...
    def save(self) -> None: ...
    def add_detail(self, detail: ExternalSalesInvoiceDetailsAttribute) -> None: ...
    def get_detail(self, detail_id: int) -> ExternalSalesInvoiceDetailsAttribute: ...
    def update_detail(self, detail_id: int, data: dict[str, Any]) -> ExternalSalesInvoiceDetailsAttribute: ...
    def delete_detail(self, detail_id: int) -> None: ...
    def list_all_by_contact_id(self, contact_id: int, state: str | None = 'all', period: str | None = 'this_year') -> list['ExternalSalesInvoice']: ...
    def create_payment(self, payment: Payment) -> None: ...
    def delete_payment(self, payment_id: int) -> None: ...

from .client import http_get as http_get
from .custom_field_model import CustomFieldModel as CustomFieldModel
from pydantic import BaseModel
from typing import Any

class ContactPerson(BaseModel):
    firstname: str | None
    lastname: str | None

class Contact(CustomFieldModel):
    company_name: str | None
    address1: str | None
    address2: str | None
    zipcode: str | None
    city: str | None
    country: str | None
    phone: str | None
    delivery_method: str | None
    customer_id: str | None
    tax_number: str | None
    firstname: str | None
    lastname: str | None
    chamber_of_commerce: str | None
    bank_account: str | None
    send_invoices_to_attention: str | None
    send_invoices_to_email: str | None
    send_estimates_to_attention: str | None
    send_estimates_to_email: str | None
    sepa_active: bool
    sepa_iban: str | None
    sepa_iban_account_name: str | None
    sepa_bic: str | None
    sepa_mandate_id: str | None
    sepa_mandate_date: str | None
    sepa_sequence_type: str | None
    si_identifier_type: str | None
    si_identifier: str | None
    invoice_workflow_id: int | None
    estimate_workflow_id: int | None
    email_ubl: bool
    direct_debit: bool
    contact_people: list[ContactPerson] | None
    type: str | None
    from_checkout: bool
    @staticmethod
    def find_by_customer_id(customer_id: str) -> Contact: ...
    def ensure_contact_people(cls, value: list[dict[str, Any] | ContactPerson] | None) -> list[ContactPerson] | None: ...

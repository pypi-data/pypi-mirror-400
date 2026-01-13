from .client import http_get as http_get
from .model import MoneybirdModel as MoneybirdModel
from typing import Self

class TaxRate(MoneybirdModel):
    name: str | None
    percentage: float | None
    tax_rate_type: str | None
    country: str | None
    active: bool | None
    administration_id: int | None
    show_tax: bool | None
    created_at: str | None
    updated_at: str | None
    @classmethod
    def list_all_rates(cls) -> list[Self]: ...
    @classmethod
    def list_sales_rates(cls) -> list[Self]: ...
    @classmethod
    def find_sales_rate_by_country(cls, country: str) -> list[Self]: ...

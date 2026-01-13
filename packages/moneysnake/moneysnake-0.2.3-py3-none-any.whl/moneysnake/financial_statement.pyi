from .financial_mutation import FinancialMutation as FinancialMutation
from .model import MoneybirdModel as MoneybirdModel
from moneysnake.client import http_patch as http_patch, http_post as http_post
from typing import Any, Self

class FinancialStatement(MoneybirdModel):
    financial_account_id: str | None
    reference: str | None
    official_date: str | None
    official_balance: str | None
    importer_service: str | None
    financial_mutations: list[FinancialMutation]
    def ensure_financial_mutations(cls, value: list[dict[str, Any]] | None) -> list[FinancialMutation] | None: ...
    def save(self) -> None: ...
    def load(self, id: int) -> None: ...
    def add_financial_mutation(self, financial_mutation: FinancialMutation) -> None: ...
    @classmethod
    def find_by_id(cls, id: int) -> Self: ...

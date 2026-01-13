from .model import MoneybirdModel as MoneybirdModel

class Payment(MoneybirdModel):
    payment_date: str | None
    price: float | None
    price_base: float | None
    financial_account_id: int | None
    financial_mutation_id: int | None
    manual_payment_action: str | None
    transaction_identifier: str | None
    ledger_account_id: int | None
    invoice_id: int | None
    def save(self) -> None: ...
    def delete(self) -> None: ...

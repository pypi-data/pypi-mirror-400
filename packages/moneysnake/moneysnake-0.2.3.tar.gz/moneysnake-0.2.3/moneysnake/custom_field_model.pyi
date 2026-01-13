from .model import MoneybirdModel as MoneybirdModel
from pydantic import BaseModel

class CustomField(BaseModel):
    id: int | None
    value: str | None

class CustomFieldModel(MoneybirdModel):
    custom_fields: list[CustomField]
    def get_custom_field(self, field_id: int) -> str | None: ...
    def set_custom_field(self, field_id: int, value: str) -> None: ...

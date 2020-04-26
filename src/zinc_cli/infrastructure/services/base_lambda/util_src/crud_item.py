from typing import Optional, Union, Dict


class CrudField:
    def __init__(self, key: str, value: str, field_type: str = "S"):
        self.field_type: str = field_type
        self.key: str = key
        self.value: str = value


class CrudItem:

    def __init__(self, pk: str, sk: Union[int, str, float, None], body: dict):

        self.user_id: Optional[str] = None
        self.pk: Optional[str] = pk  # Partition Key
        self.sk: Union[int, str, float, None] = sk  # Sort Key

        self.fields: Dict[str, CrudField] = {
            k: CrudField(k, v, "S") for k, v in body.items()
        } if body is not None else {}

    def get_field(self, field_key: str) -> CrudField:
        return self.fields[field_key]

    def from_ddb_item(self, payload: dict):
        pass

    def to_ddb_item(self):
        payload: dict = {
            "pk": {"S": self.pk},
            "sk": {"S": self.sk}
        }

        for k, field in self.fields.items():
            payload[field.key] = {field.field_type: field.value}

        return payload

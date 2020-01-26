from typing import Dict, List

from .infrastructure_service_field import InfrastructureServiceField as Field


class InfrastructureServiceModel:
    def __init__(self):
        self._all_fields: Dict[str, Field] = {}

        # General.
        self.aws_account_id: Field = self._add_field("Z_AWS_ACCOUNT_ID")
        self.aws_region: Field = self._add_field("Z_AWS_REGION")
        self.project_name: Field = self._add_field("Z_PROJECT_NAME")

        # Static site creation.
        self.static_site_domain: Field = Field("Z_STATIC_SITE_DOMAIN")

    def _add_field(self, key: str, default: str = "") -> Field:
        field = Field(key, default)
        self._all_fields[key] = field
        return field

    def save_to_environ(self):
        for field in self._all_fields.values():
            field.write_to_environ()

    def load_from_environ(self):
        for field in self._all_fields.values():
            field.load_from_environ()

    def append(self, new_model: 'InfrastructureServiceModel'):

        # Absorb the edited fields from the new model.
        for k, field in self._all_fields.items():
            new_field = new_model._all_fields[k]
            if new_field.was_edited:
                field.set(new_field.value)

    def get_command_line_args(self) -> str:
        # Turn all the non-default fields into environment arguments.
        commands: List[str] = []
        for field in self._all_fields.values():
            if field.was_edited:
                commands.append(f"{field.key}={field.value}")

        return " ".join(commands)

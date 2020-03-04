from typing import Dict, Union

import kix

from .infrastructure_service_field import InfrastructureServiceField as Field


class InfrastructureServiceModel:
    def __init__(self):
        self._all_fields: Dict[str, Field] = {}

        # General.
        self.aws_account_id: Field = self._add_field("Z_AWS_ACCOUNT_ID")
        self.aws_region: Field = self._add_field("Z_AWS_REGION")
        self.project_name: Field = self._add_field("Z_PROJECT_NAME")

        # Static Site Creation.
        self.create_static_site: Field = self._add_field("Z_CREATE_STATIC_SITE", default=False)
        self.domain_name: Field = self._add_field("Z_DOMAIN_NAME")
        self.static_site_bucket_name: Field = self._add_field("Z_STATIC_SITE_BUCKET")

        # CRUD API Creation.
        self.create_crud_api: Field = self._add_field("Z_CREATE_CRUD_API", default=False)

        # Contact Form API Creation.
        self.create_contact_api: Field = self._add_field("Z_CREATE_CONTACT_API", default=False)
        self.forwarding_email: Field = self._add_field("Z_FORWARDING_EMAIL")

    def _add_field(self, key: str, default: Union[str, bool] = "") -> Field:
        field = Field(key, default)
        self._all_fields[key] = field
        return field

    def save_to_environ(self):
        for field in self._all_fields.values():
            field.write_to_environ()

    def load_from_environ(self):
        data = {}
        for field in self._all_fields.values():
            field.load_from_environ()
            data[field.key] = field.value

        kix.info("Loading Infrastructure Model from Environment", data)

    def append(self, new_model: 'InfrastructureServiceModel'):

        # Absorb the edited fields from the new model.
        for k, field in self._all_fields.items():
            new_field = new_model._all_fields[k]
            if new_field.was_edited:
                field.set(new_field.value)

    def get_command_line_args(self) -> str:
        # Turn all the non-default fields into environment arguments.
        commands: Dict[str, str] = self.get_command_line_dict()
        commands_list = [f"{k}={v}" for k, v in commands.items()]
        return " ".join(commands_list)

    def get_command_line_dict(self) -> Dict[str, str]:
        # Turn all the non-default fields into environment arguments.
        commands: Dict[str, str] = {}
        for field in self._all_fields.values():
            if field.was_edited:
                commands[field.key] = str(field.value)
        return commands

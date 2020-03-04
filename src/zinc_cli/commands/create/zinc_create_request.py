import argparse
from typing import Optional
import kix


class ZincCreateRequest:

    def __init__(self):

        # Core project arguments.
        self.project_name: str = "untitled"
        self.domain: str = "blah.com"

        # Service APIs.
        self.with_contact_api: bool = True
        self.forwarding_email: Optional[str] = None

        # Meta-data flags.
        self.dry_run: bool = True
        self.wizard: bool = False

    def gather_arguments(self):
        self._capture_cli_arguments()
        self._execute_wizard()
        self._validation()
        self._show_arguments()
        return self

    def _capture_cli_arguments(self):
        parser = argparse.ArgumentParser()

        # Basic.
        parser.add_argument("-n", "--name", type=str, required=True, help="Name of the new project.")
        parser.add_argument("--domain", type=str, required=True, help="Bootstrap a static site at the domain.")

        # Contact API.
        parser.add_argument("--with-contact-api", action="store_true",
                            help="Whether or not to attach the contact form API.")
        parser.add_argument("--forwarding-email", type=str, help="Email to forward contact requests to.")

        # Options.
        parser.add_argument("--dry-run", action="store_true", help="Do not publish to actual AWS.")
        parser.add_argument("--wizard", action="store_true", help="On-board with the wizard.")
        args = parser.parse_args()

        self.project_name: str = args.name
        self.domain: str = args.domain
        self.with_contact_api: str = args.with_contact_api
        self.forwarding_email: str = args.forwarding_email
        self.dry_run: bool = args.dry_run
        self.wizard: bool = args.wizard

    def _execute_wizard(self):
        # Step by step input for each of the arguments.
        kix.info(f"Executing Wizard: {self.wizard}")
        if not self.wizard:
            return

        self.domain = kix.prompt.show_text_input(f"Enter domain name")

        if kix.prompt.show_yes_no("Would you like to enable contact form API?"):
            self.with_contact_api = True
            self.forwarding_email = kix.prompt.show_text_input("Contact form forwarding email")

        self.dry_run = kix.prompt.show_yes_no("Is this a dry-run?")

        kix.warning("Wizard is not implemented yet.")

    def _validation(self):
        if self.with_contact_api and not self.forwarding_email:
            message = "Cannot have a contact form if forwarding_email is empty. Please use --forwarding-email."
            kix.error(message)
            raise Exception(message)

    def _show_arguments(self):
        data = {
            "Project Name": self.project_name,
            "Domain": self.domain,
            "Contact API": {
                "Enabled": self.with_contact_api,
                "Forwarding Email": self.forwarding_email
            },
            "Dry Run": self.dry_run
        }
        kix.info("Running Zinc Create with Arguments", data)

import argparse
import kix


class ZincCreateRequest:

    def __init__(self):

        # Core project arguments.
        self.project_name: str = "untitled"
        self.domain: str = "blah.com"

        # Service APIs.
        self.with_contact_api: bool = True

        # Meta-data flags.
        self.dry_run: bool = True
        self.wizard: bool = False

    def gather_arguments(self):
        self._capture_cli_arguments()
        self._execute_wizard()

    def _capture_cli_arguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-n", "--name", type=str, required=True, help="Name of the new project.")
        parser.add_argument("--domain", type=str, required=True, help="Bootstrap a static site at the domain.")
        parser.add_argument("--with-contact-api", action="store_true",
                            help="Whether or not to attach the contact form API.")
        parser.add_argument("--dry-run", action="store_true", help="Do not publish to actual AWS.")
        parser.add_argument("--wizard", action="store_true", help="On-board with the wizard.")
        args = parser.parse_args()

        self.project_name: str = args.name
        self.domain: str = args.domain
        self.with_contact_api: str = args.with_contact_api

        self.dry_run: bool = args.dry_run
        self.wizard: bool = args.wizard

        kix.info(f"Project Name: {self.project_name}")
        kix.info(f"Domain Name: {self.domain}")
        kix.info(f"Dry-run: {str(self.dry_run)}")

    def _execute_wizard(self):
        # Step by step input for each of the arguments.
        if self.wizard:
            return

        kix.warning("Wizard is not implemented yet.")

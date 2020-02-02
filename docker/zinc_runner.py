import os
import subprocess
import zinc_cli
from zinc_cli.commands.create.static_site.create_static_site_request import CreateStaticSiteRequest
import kix


def main():
    kix.info("Starting Zinc Runner")

    env_access_key = "AWS_ACCESS_KEY_ID"
    env_secret_key = "AWS_SECRET_ACCESS_KEY"
    env_region = "AWS_REGION"

    # Validate Variables.
    env_keys = [env_access_key, env_secret_key, env_region]
    kix.info("Validating AWS Credentials")
    for k in env_keys:
        if k not in os.environ:
            error_message = f"Missing environment variable: {k}. Please provide this value."
            kix.warning(error_message)
            os.environ[k] = kix.prompt.show_text_input(k)

        kix.info(f"{k}: {os.environ[k]}")

    # Set the AWS CLI.
    os.system(f"aws configure set aws_access_key_id {os.environ[env_access_key]}")
    os.system(f"aws configure set aws_secret_access_key {os.environ[env_secret_key]}")
    os.system(f"aws configure set default.region {os.environ[env_region]}")

    kix.info("AWS CLI Configured")
    create_static_site()


def command_loop():
    pass


def create_static_site():

    kix.info("Change Directory to Zinc Workspace")
    os.chdir("/workspace")

    project_name = kix.prompt.show_text_input("Enter Project Name")
    site_domain = kix.prompt.show_text_input("Enter Domain Name (root only)")
    sub_domain = kix.prompt.show_text_input("Enter Subdomain Name [Press ENTER to skip]")
    dry_run_bool = kix.prompt.show_yes_no("Is this a dry-run?")

    dry_run_cmd = "--dry-run" if dry_run_bool else ""
    sub_domain_cmd = f"--sub-domain {sub_domain}" if len(sub_domain) > 0 else ""
    zinc_command = f"zinc-create --name {project_name} --static-site {site_domain} {sub_domain_cmd} {dry_run_cmd}"

    kix.info(f"Executing Command: {zinc_command}")
    os.system(zinc_command)


if __name__ == "__main__":
    main()

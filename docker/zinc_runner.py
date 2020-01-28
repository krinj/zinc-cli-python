import os
import subprocess
import zinc_cli
from zinc_cli.commands.create.static_site.create_static_site_request import CreateStaticSiteRequest


def main():
    print("Start Zinc Runner...")

    env_access_key = "AWS_ACCESS_KEY_ID"
    env_secret_key = "AWS_SECRET_ACCESS_KEY"
    env_region = "AWS_REGION"

    # Validate Variables.
    env_keys = [env_access_key, env_secret_key, env_region]
    print("\nValidating AWS Credentials...")
    for k in env_keys:
        if k not in os.environ:
            raise Exception(f"Missing environment variable: {k}. Please provide docker with this variable.")
        print(f"{k}: {os.environ[k]}")

    # Set the AWS CLI.
    os.system(f"aws configure set aws_access_key_id {os.environ[env_access_key]}")
    os.system(f"aws configure set aws_secret_access_key {os.environ[env_secret_key]}")
    os.system(f"aws configure set default.region {os.environ[env_region]}")
    print("AWS CLI Configured.")

    create_static_site()


def command_loop():
    pass


def create_static_site():
    project_name = input("Enter Project Name: ")
    site_domain = input("Enter Domain Name: ")
    sub_domain = input("Enter Subdomain [Press ENTER to skip]: ")
    dry_run = input("Dry-run [y/n]: ")
    dry_run_bool = True if dry_run == "y" else False
    dry_run_cmd = "--dry-run" if dry_run_bool else ""
    sub_domain_cmd = f"--sub-domain {sub_domain}" if len(sub_domain) > 0 else ""
    zinc_command = f"zinc-create --name {project_name} --static-site {site_domain} {sub_domain_cmd} {dry_run_cmd}"
    print(f"Executing: {zinc_command}")
    # request = CreateStaticSiteRequest(project_name, site_domain, sub_domain)
    # zinc_cli.zinc_create.create_static_site(project_name, site_domain, dry_run_bool)
    os.system(zinc_command)


if __name__ == "__main__":
    main()
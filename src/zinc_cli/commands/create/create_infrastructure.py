import os
import subprocess
import kix

from zinc_cli.infrastructure.models.infrastructure_service_model import InfrastructureServiceModel


def create_infrastructure(service_model: InfrastructureServiceModel, dry_run: bool):

    # Switch to infrastructure directory.
    current_path = _switch_to_infrastructure_path()

    # Create the infrastructure.
    _execute_infrastructure_command(dry_run, service_model)

    # Return to the previous path.
    os.chdir(current_path)
    kix.info(f"Execution Complete. Changed directory back to {current_path}.")


def _execute_infrastructure_command(dry_run, service_model):

    # Assemble the command.
    env_map = service_model.get_command_line_dict()
    deploy_command = "deploy" if dry_run is False else "synth"
    final_command = f"cdk {deploy_command} --require-approval never"
    kix.info(f"Executing command: {final_command}")

    # Prepare the environment variables for the sub process.
    env_map.update(os.environ.copy())

    # Run the command.
    result = subprocess.run(final_command.split(" "), env=env_map)
    kix.info(f"Executed result: {result}")


def _switch_to_infrastructure_path():
    module_path = os.path.dirname(__file__)
    current_path = os.getcwd()
    infrastructure_path = os.path.join(module_path, "..", "..", "infrastructure")
    os.chdir(infrastructure_path)
    kix.info(f"Changed directory to {infrastructure_path} to execute CDK.")
    return current_path

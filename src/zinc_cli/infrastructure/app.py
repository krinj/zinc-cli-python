#!/usr/bin/env python3

from aws_cdk import core
from services.bookings.cdk_bookings_stack import CDKBookingsStack
import os

app = core.App()
project_id = "my_new_project"

if "PROJECT_NAME" in os.environ:
    project_id = os.environ["PROJECT_NAME"]
    print(f"Project Name Override: {project_id}")

CDKBookingsStack(app, f"ZincBookings-{project_id}", project_id)

# Synthesize the application.
app.synth()

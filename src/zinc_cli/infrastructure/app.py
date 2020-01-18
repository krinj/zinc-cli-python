#!/usr/bin/env python3

from aws_cdk import core
from services.bookings.cdk_bookings_stack import CDKBookingsStack

app = core.App()
project_id = "my_new_project"
CDKBookingsStack(app, "bookings", project_id)

# Synthesize the application.
app.synth()

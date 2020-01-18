# zinc-cli-python
A headless content manager CLI.

## Overview

Zinc will be a downloadable CLI you can use to create and update a headless CMS system. It can be downloaded and installed via pip, and  can be used as an interactive terminal, command line, SDK. It will integrate with your AWS account.

## Architecture

* **Core Content Management System: ** will store content locally for the editor as mark-up files (e.g. `yaml`). The user can edit it there and then sync it with a database online.
* **Static Site Generator:** a separate process can be used to read all the content files and build them into a template and then deploy them as a static site. For now the style and theme is static, but we'll create a system to customise them too. For this, we can perhaps inject the data into an existing static site template, and use it to deploy.
* **API Manager: ** will also be an API definition and API creator for things like bookings, admin and interactive systems
* **Automation Tools:** There will be a custom dashboard system for managing all of these tools.
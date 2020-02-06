# zinc-cli-python
A headless content manager CLI.

## Overview

Zinc will be a downloadable CLI you can use to create and update a headless CMS system. It can be downloaded and installed via pip, and  can be used as an interactive terminal, command line, SDK. It will integrate with your AWS account.

## Architecture

* **Core Content Management System: ** will store content locally for the editor as mark-up files (e.g. `yaml`). The user can edit it there and then sync it with a database online.
* **Static Site Generator:** a separate process can be used to read all the content files and build them into a template and then deploy them as a static site. For now the style and theme is static, but we'll create a system to customise them too. For this, we can perhaps inject the data into an existing static site template, and use it to deploy.
* **API Manager: ** will also be an API definition and API creator for things like bookings, admin and interactive systems
* **Automation Tools:** There will be a custom dashboard system for managing all of these tools.

## Requirements

[Python 3.7](https://docs.conda.io/en/latest/miniconda.html): You will first need a Python 3.7 environment to use this CLI. Install a virtual environment for Python 3.7 by following one of the instructions above. I recommend [Miniconda](https://docs.conda.io/en/latest/miniconda.html), but you can also use another Python 3.7 environment if you wish

[AWS Account](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/): You will need this to host your project.

[AWS IAM User](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html#id_users_create_console): To configure your AWS CLI, you will need an IAM user (public key and secret key). Go ahead and create one with admin rights.

[AWS CLI](https://aws.amazon.com/cli/): You need this to configure your AWS Account.

[AWS CDK](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html): This will be used by the CLI to deploy your infrastructure. The CDK itself requires Node and NPM to be installed.

## Installation

#### Python CLI

Once you have all of the above requirements, activate your Python 3.7 environment (the same one you installed the AWS CLI to) and install zinc.

```bash
pip install zinc-cli
```

#### With Conda (Linux)

Follow these steps if you don't know how to install or activate a Miniconda environment.

1. Download Miniconda.

   ```bash
   wget -O miniconda.sh "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
   ```

2. Install Miniconda.

   ```bash
   # Follow the prompts.
   sh miniconda.sh
   
   # Or do this if you don't want prompts.
   sh miniconda.sh -b -p $HOME/miniconda
   ```

3. Initialise Miniconda.

   ```bash
   ~/miniconda/bin/conda init
   ```

4. Create Python environment named `zinc`.

   ```bash
   conda create --name zinc python=3.7
   ```

5. Activate zinc environment.

   ```bash
   source activate zinc
   ```

6. Install Zinc CLI.

   ```bash
   pip install zinc-cli
   ```

## Create Static Site

This command will create a static site bucket for you. Before you can use this, you must register the domain name you want to use on [AWS Route53](https://aws.amazon.com/route53/) in your AWS account. The static site creation will do the following:

* Creates an S3 bucket that contains your static site resources. Must contain `index.html` as the entry point.
* Links your provided domain name to the bucket, and uses CloudFront to route it with HTTPS access.

```bash
# Command Format
zinc-create --name <project-name> --static-site <domain-name>

# Example
zinc-create --name helloworld --static-site helloworld.com

# To dry-run (test the command but do not actually create resources):
zinc-create --name helloworld --static-site helloworld.com --dry-run
```

This process could take a while — especially for AWS to register and hook up the certificate. When it is done you will have the resources available on your AWS account.

> **NOTE**: The command could take up to an hour to execute, as it tries to create the Site Distribution resource.

## Running With Docker in 3 Steps

This should only take about 15-20 minutes to set up, and should work on all platforms.

1. [Install Docker](https://docs.docker.com/install/)

2. Download the latest `zinc-cli` docker image:

   ```bash
   docker pull infrarift/zinc
   ```

3. Run with your IAM AWS credentials or just vanilla:

   ```bash
   # Run with your environment variables.
   docker run -e AWS_ACCESS_KEY_ID=<YOUR_KEY> -e AWS_SECRET_ACCESS_KEY=<YOUR_SECRET> -e AWS_REGION=<YOUR_DEFAULT_REGION> --volume ${PWD}:/workspace -i infrarift/zinc
   
   # Example.
   docker run -e AWS_ACCESS_KEY_ID=AKIHJEUAXXXXXE7IIAIA -e AWS_SECRET_ACCESS_KEY=GxDhPPQUtV4grDqx2kswXXXXXXXXXXXXXXXXXXXX -e AWS_REGION=us-west-2 --volume ${PWD}:/workspace -i infrarift/zinc
   
   # Without Environments.
   docker run --volume ${PWD}:/workspace -i infrarift/zinc:latest
   ```

Follow the prompts in the container to create and deploy the project
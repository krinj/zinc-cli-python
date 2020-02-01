FROM node:13

# Install Miniconda for Python 3.7
RUN apt-get update
RUN wget -O miniconda.sh "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
RUN sh miniconda.sh -b -p /root/miniconda
ENV PATH "/root/miniconda/bin:$PATH"

# Install AWS CLI
RUN pip install awscli

# Install AWS CDK
RUN npm install -g cdk@1.22.0

# Install Zinc CLI (UPDATE 1)
RUN pip install --upgrade zinc-cli==0.0.54
RUN pip install --upgrade kix==0.1.5

# Copy the runner script.
ADD zinc_runner.py .

# Run the script
ENTRYPOINT [ "python", "zinc_runner.py" ]


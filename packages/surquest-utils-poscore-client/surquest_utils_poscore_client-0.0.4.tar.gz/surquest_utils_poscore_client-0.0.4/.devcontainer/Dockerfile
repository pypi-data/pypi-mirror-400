FROM python:3.14-slim

# Install git and other common tools
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*


# Create workspace directory
RUN mkdir -p /workspace

# Set working directory
WORKDIR /workspace

# Install pip 
RUN pip install --upgrade pip


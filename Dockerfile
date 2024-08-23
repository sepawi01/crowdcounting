# Use the official PyTorch runtime image with CUDA and cuDNN
FROM pytorch/pytorch:2.4.0-cuda12.4-cudnn9-runtime

# Set a working directory inside the container
WORKDIR /app

# Install all necessary packages in a single RUN statement
RUN apt-get update && \
    apt-get install -y curl gnupg2 apt-transport-https ca-certificates && \
    curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.gpg && \
    curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y DEBIAN_FRONTEND=noninteractive apt-get install -y unixodbc unixodbc-dev libsqlite3-dev python3-dev build-essential msodbcsql17 mssql-tools && \
    apt-get clean && \
    echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY . .


# Set the default command to run your Python script
CMD ["python", "main.py"]

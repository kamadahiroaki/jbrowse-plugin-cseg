FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the project files
COPY . .

# Install Python dependencies and build the package
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip \
    && pip install pybind11 \
    && pip install flask-cors pillow numpy matplotlib tqdm \
    && pip install -e .

# Expose port for cseg-server
EXPOSE 5000

# Command to run the cseg-server
CMD ["cseg-server"]

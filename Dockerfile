FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    sqlite3 \
    libomp-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the project files
COPY . .

# Install Python dependencies and build the package
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install pybind11 first and verify its installation
RUN pip install --upgrade pip \
    && pip install pybind11 \
    && python -c "import pybind11; print('pybind11 include path:', pybind11.get_include())"

# Install other dependencies and build the package with verbose output
RUN pip install flask-cors pillow numpy matplotlib tqdm \
    && CFLAGS="-I$(python -c 'import pybind11; print(pybind11.get_include())')" \
       VERBOSE=1 pip install -e . \
    && python -c "import cseg.lib.cseg_renderer; print('cseg_renderer successfully imported')" \
    && python -c "import cseg.bin.vcf2cseg_cpp; print('vcf2cseg_cpp successfully imported')"

# Create data directories
RUN cseg-init

# Test if commands are available and verify their functionality
RUN which vcf2cseg && \
    which cseg-create-db && \
    which cseg-server && \
    ls -l /opt/venv/lib/python3.10/site-packages/cseg/lib/cseg_renderer*.so && \
    ls -l /opt/venv/lib/python3.10/site-packages/cseg/bin/vcf2cseg_cpp*.so

# Expose port for cseg-server
EXPOSE 5000

# Command to run the cseg-server
CMD ["cseg-server"]

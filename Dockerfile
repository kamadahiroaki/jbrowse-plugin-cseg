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

# Install other dependencies and build the package
RUN pip install flask-cors pillow numpy matplotlib tqdm \
    && CFLAGS="-I$(python -c 'import pybind11; print(pybind11.get_include())')" pip install -e . \
    && python -c "from cseg.lib import cseg_renderer; print('cseg_renderer successfully imported')"

# Test if commands are available
RUN which vcf2cseg && \
    which cseg-create-db && \
    which cseg-server

# Expose port for cseg-server
EXPOSE 5000

# Command to run the cseg-server
CMD ["cseg-server"]

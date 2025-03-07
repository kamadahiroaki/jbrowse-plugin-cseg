FROM debian:bookworm-slim

# Install Python and system dependencies with retry logic
RUN apt-get update && \
    for i in $(seq 1 5); do \
        apt-get install -y \
            python3.11 \
            python3.11-dev \
            python3.11-venv \
            build-essential \
            g++ \
            sqlite3 \
            libomp-dev \
        && break || { \
            if [ $i -lt 5 ]; then \
                echo "Attempt $i failed! Retrying in 5 seconds..."; \
                sleep 5; \
                apt-get update; \
            else \
                echo "Failed after 5 attempts!"; \
                exit 1; \
            fi \
        } \
    done \
    && rm -rf /var/lib/apt/lists/*

# Set user ID and group ID
ARG USER_ID=1000
ARG GROUP_ID=1000

# Create group and user
RUN groupadd -g $GROUP_ID cseg && \
    useradd -u $USER_ID -g $GROUP_ID -m cseg

# Set working directory
WORKDIR /app

# Copy the project files
COPY . .

# Install Python dependencies and build the package
RUN python3.11 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install pybind11 first
RUN pip install --upgrade pip \
    && pip install pybind11 \
    && python -c "import pybind11; print('pybind11 include path:', pybind11.get_include())"

# Install the package and build C++ extensions
RUN pip install flask-cors pillow numpy matplotlib tqdm \
    && echo "Building and installing package..." \
    && CFLAGS="-v" pip install . \
    && echo "Build directory contents:" \
    && ls -R build \
    && echo "Site-packages contents:" \
    && ls -R /opt/venv/lib/python3.11/site-packages/cseg \
    && echo "Cleaning up source directory..." \
    && cd / \
    && rm -rf /app/* \
    && echo "Verifying installation:" \
    && python -c "from cseg.lib import cseg_renderer; print('cseg_renderer imported successfully')" \
    && python -c "from cseg.bin import vcf2cseg_cpp; print('vcf2cseg_cpp imported successfully')"

# Create data directories
RUN cseg-init

# Create data directory and set ownership
RUN mkdir -p /data/cseg && chown -R cseg:cseg /data/cseg

# Set working directory to a clean location
WORKDIR /srv

# Switch to user
USER cseg

# Expose port for cseg-server
EXPOSE 5000

# Command to run the cseg-server
CMD ["cseg-server"]

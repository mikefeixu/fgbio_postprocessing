FROM python:3.9-slim

LABEL org.opencontainers.image.source="https://github.com/mikefeixu/fgbio_postprocessing"
LABEL org.opencontainers.image.description="fgbio postprocessing tools including simplex_filter"
LABEL org.opencontainers.image.version="0.3.0"

# Install build dependencies for pysam (requires htslib C headers)
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libc6-dev \
        zlib1g-dev \
        libbz2-dev \
        liblzma-dev \
        libcurl4-openssl-dev \
        libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install the package
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install --no-cache-dir .

# Verify the entry point is available
RUN simplex_filter --help

CMD ["simplex_filter"]

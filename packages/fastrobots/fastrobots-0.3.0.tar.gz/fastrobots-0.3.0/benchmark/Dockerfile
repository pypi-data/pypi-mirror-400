FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Rust for building fastrobots
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Upgrade pip
RUN pip3 install --upgrade pip

# Install reppy (should work on Ubuntu 20.04)
RUN pip3 install reppy

# Install maturin for building fastrobots
RUN pip3 install maturin httpx click

# Copy fastrobots source
WORKDIR /app
COPY Cargo.toml Cargo.lock ./
COPY src ./src
COPY python ./python

# Create a modified pyproject.toml with Python 3.8 support
RUN echo '[project]\n\
name = "fastrobots"\n\
version = "0.3.0"\n\
description = "Blazingly fast robots.txt parser"\n\
requires-python = ">=3.8"\n\
dependencies = ["httpx>=0.24.0", "click>=8.0.0"]\n\
\n\
[build-system]\n\
requires = ["maturin>=1.0"]\n\
build-backend = "maturin"\n\
\n\
[tool.maturin]\n\
features = ["pyo3/extension-module"]\n\
python-source = "python"\n\
module-name = "fastrobots._core"\n' > pyproject.toml

RUN echo "# fastrobots" > README.md

# Build fastrobots
RUN maturin build --release && pip3 install target/wheels/*.whl

# Copy benchmark script
COPY benchmark/bench.py ./bench.py

CMD ["python3", "bench.py"]

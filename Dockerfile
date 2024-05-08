FROM nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04

ENV PYTHON_VERSION=3.10

RUN apt-get update && apt-get install -y \
    git \
    git-lfs \
    curl \
    wget \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y \
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-dev \
    python${PYTHON_VERSION}-distutils \
    && update-alternatives --install /usr/bin/python python /usr/bin/python${PYTHON_VERSION} 1 \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl -ss https://bootstrap.pypa.io/get-pip.py | python${PYTHON_VERSION}

CMD ["bash"]
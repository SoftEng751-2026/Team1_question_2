FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    build-essential \
    dos2unix \
    openjdk-11-jdk \
    python3 \
    python3-pip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
    pandas==2.2.0 \
    matplotlib==3.5.0

WORKDIR /app
COPY . .
RUN dos2unix run_tests.sh
CMD ["bash", "-c", "./run_tests.sh && python3 create_plot.py"]
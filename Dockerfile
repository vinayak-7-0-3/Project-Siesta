FROM python:3.12-slim AS base

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Kolkata

WORKDIR /usr/src/app

RUN apt-get update -qq && \
    apt-get install -qq -y ffmpeg gcc libffi-dev && \
    rm -rf /var/lib/apt/lists/*

# Install build dependencies and rclone in a separate stage
FROM base AS builder
RUN apt-get update -qq && \
    apt-get install -qq -y git wget curl unzip && \
    rm -rf /var/lib/apt/lists/*

# Download and install rclone
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then ARCH="amd64"; \
    elif [ "$ARCH" = "aarch64" ]; then ARCH="arm64"; fi && \
    curl -O https://downloads.rclone.org/v1.68.2/rclone-v1.68.2-linux-${ARCH}.zip && \
    unzip rclone-v1.68.2-linux-${ARCH}.zip && \
    install -m 755 rclone-v1.68.2-linux-${ARCH}/rclone /usr/bin/rclone && \
    rm -rf rclone-v1.68.2-linux-${ARCH}*

# Final stage with only necessary files
FROM base AS final

COPY --from=builder /usr/bin/rclone /usr/bin/rclone

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "-m", "bot"]
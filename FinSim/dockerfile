FROM ubuntu:22.04

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_ROOT_USER_ACTION=ignore
ENV GRADLE_OPTS="-Dorg.gradle.daemon=false -Dorg.gradle.jvmargs=-Xmx1024m"

# Android / Flutter dépendances
RUN apt-get update && apt-get install -y \
    curl git unzip xz-utils zip libglu1-mesa python3 python3-pip openjdk-17-jdk \
    && rm -rf /var/lib/apt/lists/*

# Fix Git
RUN git config --global --add safe.directory "*"

# Installer flet
RUN pip3 install --upgrade pip && pip3 install flet==0.28.3

# Copier le projet
COPY . .

# Installer dépendances Python
RUN pip3 install -r requirements.txt || true

# Build APK
CMD ["flet", "build", "apk", "--verbose"]
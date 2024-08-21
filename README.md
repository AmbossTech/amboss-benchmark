# Amboss Pathfinding Benchmark

## Overview

This project contains a script for benchmarking Amboss' pathfinding endpoint against LND.
Using the top 1000 nodes (by capacity) as destinations, this script queries both LND and Reflex for a path. It then probes
each path and records the results in `/output`.

## Prerequisites

Before you can run this project, ensure you have the following installed on your machine:

- **[Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)**: To clone the repository from GitHub.
- **[Docker](https://docs.docker.com/get-docker/)**: To build and run the application in a containerized environment.
- **[Docker Compose](https://docs.docker.com/compose/install/)**: To manage multi-container Docker applications.

## Getting Started

Follow the steps below to pull the project from GitHub and run it using Docker.

### 1. Clone the Repository

First, clone the repository to your local machine using the following command:

```bash
git clone https://github.com/AmbossTech/amboss-benchmark.git
```

### 2. Navigate to the Project Directory

Change into the directory of the cloned project:

```bash
cd amboss-benchmark
```

### 3. Set up the environment

Copy the example environment file:

```bash
cp .env-example .env
```

Open the `.env` file and add the following:

- `MACAROON_HEX` - hex encoded LND macaroon string used to query/probe routes in LND.
- `LND_SOCKET` - address of LND node.
- `LND_PUBKEY` - public key of LND node.
- `REFLEX_API_KEY` - api key used to query paths from Reflex

### 4. Build the Docker Image

Build the Docker image using the `docker-compose.yml` file included in the project:

```bash
docker-compose build
```

This command will read the `Dockerfile` and build an image tagged as `reflex-benchmark:latest`.

### 5. Run the Application

To start the application, use the following command:

```bash
docker-compose up
```

This command will start the container, running the application as defined in the `docker-compose.yml` file.

### 6. Stopping the Application

To stop the application manually, press `Ctrl+C` in the terminal where the application is running. If you started the
container
in detached mode (using `-d`), you can stop it with:

```bash
docker-compose down
```

This command will stop and remove the container, but the Docker image and volumes will persist.


---


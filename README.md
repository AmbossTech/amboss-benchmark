# Amboss Pathfinding Benchmark

## Overview

On May 20th, 2024, Amboss released [research](https://arxiv.org/abs/2405.12087) on predicting channel balances for use in pathfinding. 
Since then, Amboss has implemented this research into a pathfinding service available through their Payment Operations platform, [Reflex](https://amboss.space/reflex/).

This project contains a script for benchmarking Amboss' pathfinding service against LND.
Using the top 1000 nodes by capacity as destinations, this script queries both LND and Reflex for a path.
The script then probes each path with a fixed size payment and records the results in `/output`.


## Prerequisites

Before you can run this project, the following are required:

- **[Amboss Account](https://amboss.space/login)**: Must have an account with Amboss.
- **[Reflex](https://amboss.space/reflex/)**: Must have access to our Reflex product. Please email pathfinding@amboss.tech and we will enable Reflex on your Amboss Account.
- **[Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)**: To clone the repository from GitHub.
- **[Docker](https://docs.docker.com/get-docker/)**: To build and run the application in a containerized environment.
- **[Docker Compose](https://docs.docker.com/compose/install/)**: To manage Docker applications.


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
- `LND_SOCKET` - clearnet address of LND node. e.g. URL or IP:PORT
- `LND_PUBKEY` - public key of LND node.
- `REFLEX_API_KEY` - API key used to query paths from Reflex. (instructions below)


#### A note about macaroons

Macaroons are a sensitive piece of information used for authentication in a Lightning Node. 
Using this software does NOT give Amboss access to any of this information. 
This script was tested using `admin.macaroon`.

To [bake a custom macaroon](https://docs.lightning.engineering/lightning-network-tools/lnd/macaroons#docs-internal-guid-7b736a99-7fff-4c6f-a308-73da0d74c992), the following permissions are required:

- `info:read`: to query routes via `QueryRoutes`
- `offchain:write`: to probe routes via `SendToRouteSync` 

#### Generating a Reflex API key

- In your Reflex Dashboard under Settings, there is an [API keys section](https://amboss.space/reflex/settings/api-keys). 
- Click the "Generate API Key" button.
- Fill out the form. In the node section, be sure to select the same pubkey as will be running the benchmark.
- In the next popup, click the button to copy the API key. NOTE: this key will only be displayed once.
- Paste the API key into `.env`.

#### Using a TLS Certificate

If your node is not on clearnet, you may need to use a `tls.cert` file for gRPC SSL credentials. 
The application will automatically use the certificate if it is provided in the project directory. 
Place the `tls.cert` file in the root directory of this project. Make sure it is named exactly `tls.cert`.

### 4. Build the Docker Image

Build the Docker image using the `docker-compose.yml` file included in the project:

```bash
docker-compose build
```

This command will read the `Dockerfile` and build an image tagged as `reflex-benchmark:latest`.
Note: you must rebuild the docker image after editing any file including `.env`. 

### 5. Run the Application

To start the application, use the following command:

```bash
docker-compose up -d
```

This command will start the container, running the application as defined in the `docker-compose.yml` file.

### 6. Stopping the Application

In detached mode (using `-d`), you can stop the docker container with:

```bash
docker-compose down
```

This command will stop and remove the container, but the Docker image and volumes will persist.


### Step 7: Returning the Results

Once you have started the program, please note that it will take a few hours to complete the execution. You can monitor the progress using the following Docker command:

```bash
docker logs -t amboss-benchmark-reflex-benchmark-1
```

While the program is running, it will periodically save benchmark results in the `/output` directory like so:

```
amboss-benchmark/outputs/benchmark_results_<timestamp>.csv
```

Please share the final results with us once the program has completed. The CSV file can be emailed to us at pathfinding@amboss.tech. 
This data you provide will help us generate a detailed report and further improve the product based on real-world performance.

---

### Directory Structure

```markdown
amboss-benchmark/
├── grpc_generated/
├── output/
├── .env-example
├── .gitignore
├── api_classes.oy
├── benchmark.py
├── docker-compose.yml
├── Dockerfile
├── lnd.py
├── path_adapter.py
├── README.md
├── requirements.txt
├── top_nodes.txt
└── utils.py
```
### Explanation of Each Directory and File

1. **`grpc_generated/`**:
   - Directory for LND gRPC files. [More info.](https://github.com/lightningnetwork/lnd/blob/master/docs/grpc/python.md)

2. **`output/`**:
   - Directory for storing results generated by the benchmarking process.

3. **`.env-example`**:
   - Example environment variable file, showing what environment variables are needed and their expected formats.

4. **`.gitignore`**:
   - Specifies files and directories to be ignored by git.

5. **`api_classes.py`**:
   - Contains class definitions for interacting with the Reflex Pathfinding API.

6. **`benchmark.py`**:
   - The main script for running the benchmark tests.

7. **`docker-compose.yml`**:
   - Configuration file for Docker Compose, used to manage Docker applications.

8. **`Dockerfile`**:
   - Contains the instructions to build the Docker image for the project, including the environment setup and dependencies.

9. **`lnd.py`**:
   - Contains functionality related to the Lightning Network Daemon (LND) for querying and probing routes.

10. **`path_adapter.py`**:
    - Implements logic for adapting JSON responses from the pathfinding endpoint into LND Routes.

11. **`README.md`**:
    - ⭐You are here.

12. **`requirements.txt`**:
    - Lists the Python dependencies required to run the project.

13. **`top_nodes.txt`**:
    - A text file containing pubkeys of the top 1000 nodes by capacity.

14. **`utils.py`**:
    - Utility functions used throughout the project.


---

### Disclaimer
This software is provided on an "as-is" and "as-available" basis, without any warranties of any kind, either express or implied.


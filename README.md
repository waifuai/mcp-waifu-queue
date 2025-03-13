# MCP Waifu Queue

This project implements an MCP (Model Context Protocol) server for a conversational AI "waifu" character, leveraging a text generation service with a Redis queue and GPU acceleration. It utilizes the `FastMCP` library for simplified server setup and management.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Service](#running-the-service)
- [MCP API](#mcp-api)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

*   Text generation using the distilgpt2 language model.
*   Request queuing using Redis for handling concurrent requests.
*   GPU support for faster inference.
*   MCP-compliant API using `FastMCP`.
*  Job status tracking.

## Architecture

The project consists of several key components:

*   **`main.py`**: The main entry point, initializing the `FastMCP` application.
*   **`respond.py`**: The core text generation service, loading the distilgpt2 model and generating responses.
*   **`queue.py`**: Handles interactions with the Redis queue, enqueuing requests and managing job IDs.
*   **`worker.py`**: A Redis worker that processes jobs from the queue, utilizing `respond.py` for text generation.
*   **`config.py`**: Manages configuration via environment variables.
*   **`models.py`**: Defines Pydantic models for request and response validation.

The flow of a request is as follows:

1.  A client sends a request to the `generate_text` MCP tool (defined in `main.py`).
2.  The tool enqueues the request to a Redis queue (handled by `queue.py`).
3.  A `worker.py` process picks up the request from the queue.
4.  The worker calls the `call_predict_response` function (in `utils.py`), which interacts with `respond.py` to generate the text.
5.  The generated text is stored, and the job status is updated.
6.  The client can retrieve the result using the `get_job_status` resource (defined in `main.py`).

## Prerequisites

*   Python 3.7+
*   pip
*   Redis server (installed and running)
*   A CUDA-enabled GPU (optional, but recommended for performance)

You can find instructions for installing Redis on your system on the official Redis website: [https://redis.io/docs/getting-started/](https://redis.io/docs/getting-started/)

## Installation

1.  Clone the repository:

    ```bash
    git clone <YOUR_REPOSITORY_URL>
    cd mcp-waifu-queue
    ```

2.  Create and activate a virtual environment:

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```

3.  Install dependencies:

    ```bash
     pip install --user -r requirements.txt #If requirements.txt exists
    ```
    Or, if using pyproject.toml
    ```bash
    pip install --user -e .
    ```

## Configuration

1.  Copy the `.env.example` file to `.env`:

    ```bash
    cp .env.example .env
    ```

2.  Modify the `.env` file to set the appropriate values for your environment. The following environment variables are available:

    *   `MODEL_PATH`: The path to the pre-trained language model (default: `distilgpt2`).
    *   `GPU_SERVICE_URL`: The URL of the GPU service (default: `http://localhost:5001`).  This is used internally by the worker.
    *   `REDIS_URL`: The URL of the Redis server (default: `redis://localhost:6379`).
    *   `QUEUE_PORT`: The port for the queue service (default: `5000`). This is no longer directly used for external access, as we're using MCP.
    *   `RESPOND_PORT`: The port for the response service (default: `5001`). This is used internally by the worker.
    *   `MAX_NEW_TOKENS`: The maximum number of new tokens to generate (default: 20).

    **Note:** The `.env` file should not be committed to the repository for security reasons.

## Running the Service

Start the services using the `scripts/start-services.sh` script:

```bash
./scripts/start-services.sh
```

This script will start the Redis server (if not already running), the worker, the queue service, and the response service. The services will run in the background.

## MCP API

The server provides the following MCP-compliant endpoints:

### Tools

*   `generate_text` (prompt: str): Sends a text generation request and returns a job ID.

### Resources

*   `job://{job_id}`: Retrieves the status of a job.  The response will include a `status` field (e.g., "queued", "processing", "completed", "failed") and, if completed, a `result` field containing the generated text.

## Testing

The project includes tests. You can run all tests using `pytest`:

```bash
pytest tests
```

## Troubleshooting

*   **Error: "Missing 'prompt' parameter"**: Make sure you are sending a prompt string to the `generate_text` tool.
*   **Error: "Error calling GPU service"**: Ensure that the `respond.py` service is running and accessible at the configured `GPU_SERVICE_URL`.
*   **Error: "Service unavailable"**: Check if Redis server, worker, queue and respond services are running.
*   **If encountering CUDA errors:** Ensure your CUDA drivers and toolkit are correctly installed and compatible with your PyTorch version.

## Contributing

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Commit your changes.
4.  Push your branch to your forked repository.
5.  Create a pull request.

Please adhere to the project's code of conduct.

## License

This project is licensed under the MIT-0 License - see the [LICENSE](LICENSE) file for details.

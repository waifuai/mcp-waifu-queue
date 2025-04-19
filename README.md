# MCP Waifu Queue (Gemini Edition)

This project implements an MCP (Model Context Protocol) server for a conversational AI "waifu" character, leveraging the Google Gemini API via a Redis queue for asynchronous processing. It utilizes the `FastMCP` library for simplified server setup and management.

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

*   Text generation using the Google Gemini API (`gemini-2.5-flash-preview-04-17`).
*   Request queuing using Redis for handling concurrent requests asynchronously.
*   MCP-compliant API using `FastMCP`.
*   Job status tracking via MCP resources.
*   Configuration via environment variables (`.env` file) and API key loading from `~/.api-gemini`.

## Architecture

The project consists of several key components:

*   **`main.py`**: The main entry point, initializing the `FastMCP` application and defining MCP tools/resources.
*   **`respond.py`**: Contains the core text generation logic using the `google-generativeai` library to interact with the Gemini API.
*   **`task_queue.py`**: Handles interactions with the Redis queue (using `python-rq`), enqueuing generation requests.
*   **`utils.py`**: Contains utility functions, specifically `call_predict_response` which is executed by the worker to call the Gemini logic in `respond.py`.
*   **`worker.py`**: A Redis worker (`python-rq`) that processes jobs from the queue, calling `call_predict_response`.
*   **`config.py`**: Manages configuration using `pydantic-settings`.
*   **`models.py`**: Defines Pydantic models for MCP request and response validation.

The flow of a request is as follows:

1.  A client sends a request to the `generate_text` MCP tool (defined in `main.py`).
2.  The tool enqueues the request (prompt) to a Redis queue (handled by `task_queue.py`).
3.  A `worker.py` process picks up the job from the queue.
4.  The worker executes the `call_predict_response` function (from `utils.py`).
5.  `call_predict_response` calls the `predict_response` function (in `respond.py`), which interacts with the Gemini API.
6.  The generated text (or an error message) is returned by `predict_response` and stored as the job result by RQ.
7.  The client can retrieve the job status and result using the `job://{job_id}` MCP resource (defined in `main.py`).

```mermaid
graph LR
    subgraph Client
        A[User/Client] -->|1. Send Prompt via MCP Tool| B(mcp-waifu-queue: main.py)
    end
    subgraph mcp-waifu-queue Server
        B -->|2. Enqueue Job (prompt)| C[Redis Queue]
        B -->|7. Return Job ID| A
        D[RQ Worker (worker.py)] --|>| C
        D -->|3. Dequeue Job & Execute| E(utils.call_predict_response)
        E -->|4. Call Gemini Logic| F(respond.predict_response)
        F -->|5. Call Gemini API| G[Google Gemini API]
        G -->|6. Return Response| F
        F --> E
        E -->|Update Job Result in Redis| C
        A -->|8. Check Status via MCP Resource| B
        B -->|9. Fetch Job Status/Result| C
        B -->|10. Return Status/Result| A
    end
```

## Prerequisites

*   Python 3.7+
*   `pip` or `uv` (Python package installer)
*   Redis server (installed and running)
*   A Google Gemini API Key

You can find instructions for installing Redis on your system on the official Redis website: [https://redis.io/docs/getting-started/](https://redis.io/docs/getting-started/)
You can obtain a Gemini API key from Google AI Studio: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

## Installation

1.  Clone the repository:

    ```bash
    git clone <YOUR_REPOSITORY_URL>
    cd mcp-waifu-queue
    ```

2.  Create and activate a virtual environment (using `venv` or `uv`):

    *Using `venv` (standard library):*
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Linux/macOS
    # .venv\Scripts\activate  # On Windows CMD
    # source .venv/Scripts/activate # On Windows Git Bash/PowerShell Core
    ```

    *Using `uv` (if installed):*
    ```bash
    # Ensure uv is installed (e.g., pip install uv)
    python -m uv venv .venv
    source .venv/bin/activate # Or equivalent activation for your shell
    ```

3.  Install dependencies (using `pip` within the venv or `uv`):

    *Using `pip`:*
    ```bash
    pip install -e .[test] # Installs package in editable mode with test extras
    ```

    *Using `uv`:*
    ```bash
    # Ensure uv is installed inside the venv if desired, or use the venv's python
    # .venv/Scripts/python.exe -m pip install uv # Example for Windows
    .venv/Scripts/python.exe -m uv pip install -e .[test] # Example for Windows
    # python -m uv pip install -e .[test] # If uv is in PATH after venv activation
    ```


## Configuration

1.  **API Key:** Create a file named `.api-gemini` in your home directory (`~/.api-gemini`) and place your Google Gemini API key inside it. Ensure the file has no extra whitespace.
    ```bash
    echo "YOUR_API_KEY_HERE" > ~/.api-gemini
    ```
    *(Replace `YOUR_API_KEY_HERE` with your actual key)*

2.  **Other Settings:** Copy the `.env.example` file to `.env`:

    ```bash
    cp .env.example .env
    ```

3.  Modify the `.env` file to set the remaining configuration values:

    *   `MAX_NEW_TOKENS`: Maximum number of tokens for the Gemini response (default: `2048`).
    *   `REDIS_URL`: The URL of your Redis server (default: `redis://localhost:6379`).
    *   `FLASK_ENV`, `FLASK_APP`: Optional, related to Flask if used elsewhere, not core to the MCP server/worker operation.

## Running the Service

1.  **Ensure Redis is running.** If you installed it locally, you might need to start the Redis server process (e.g., `redis-server` command, or via a service manager).

2.  **Start the RQ Worker:**
    Open a terminal, activate your virtual environment (`source .venv/bin/activate` or similar), and run:
    ```bash
    python -m mcp_waifu_queue.worker
    ```
    This command starts the worker process, which will listen for jobs on the Redis queue defined in your `.env` file. Keep this terminal running.

3.  **Start the MCP Server:**
    Open *another* terminal, activate the virtual environment, and run the MCP server using a tool like `uvicorn` (you might need to install it: `pip install uvicorn` or `uv pip install uvicorn`):
    ```bash
    uvicorn mcp_waifu_queue.main:app --reload --port 8000 # Example port
    ```
    Replace `8000` with your desired port. The `--reload` flag is useful for development.

    Alternatively, you can use the `start-services.sh` script (primarily designed for Linux/macOS environments) which attempts to start Redis (if not running) and the worker in the background:
    ```bash
    # Ensure the script is executable: chmod +x ./scripts/start-services.sh
    ./scripts/start-services.sh
    # Then start the MCP server manually as shown above.
    ```

## MCP API

The server provides the following MCP-compliant endpoints:

### Tools

*   **`generate_text`**
    *   **Description:** Sends a text generation request to the Gemini API via the background queue.
    *   **Input:** `{"prompt": "Your text prompt here"}` (Type: `GenerateTextRequest`)
    *   **Output:** `{"job_id": "rq:job:..."}` (A unique ID for the queued job)

### Resources

*   **`job://{job_id}`**
    *   **Description:** Retrieves the status and result of a previously submitted job.
    *   **URI Parameter:** `job_id` (The ID returned by the `generate_text` tool).
    *   **Output:** `{"status": "...", "result": "..."}` (Type: `JobStatusResponse`)
        *   `status`: The current state of the job (e.g., "queued", "started", "finished", "failed"). RQ uses slightly different terms internally ("started" vs "processing", "finished" vs "completed"). The resource maps these.
        *   `result`: The generated text from Gemini if the job status is "completed", otherwise `null`. If the job failed, the result might be `null` or contain error information depending on RQ's handling.

## Testing

The project includes tests. Ensure you have installed the test dependencies (`pip install -e .[test]` or `uv pip install -e .[test]`).

Run tests using `pytest`:

```bash
pytest tests
```

**Note:** Tests might require mocking Redis (`fakeredis`) and potentially the Gemini API calls depending on their implementation.

## Troubleshooting

*   **Error: `Gemini API key not found in .../.api-gemini or GEMINI_API_KEY environment variable`**: Ensure you have created the `~/.api-gemini` file in your home directory and placed your valid Gemini API key inside it. Alternatively, ensure the `GEMINI_API_KEY` environment variable is set as a fallback.
*   **Error during Gemini API call (e.g., AuthenticationError, PermissionDenied)**: Double-check that the API key in `~/.api-gemini` (or the fallback environment variable) is correct and valid. Ensure the API is enabled for your Google Cloud project if applicable.
*   **Jobs stuck in "queued"**: Verify that the RQ worker (`python -m mcp_waifu_queue.worker`) is running in a separate terminal and connected to the same Redis instance specified in `.env`. Check the worker logs for errors.
*   **ConnectionRefusedError (Redis)**: Make sure your Redis server is running and accessible at the `REDIS_URL` specified in `.env`.
*   **MCP Server Connection Issues**: Ensure the MCP server (`uvicorn ...`) is running and you are connecting to the correct host/port.

## Contributing

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix (`git checkout -b feature/your-feature-name`).
3.  Make your changes and commit them (`git commit -am 'Add some feature'`).
4.  Push your branch to your forked repository (`git push origin feature/your-feature-name`).
5.  Create a new Pull Request on the original repository.

Please adhere to the project's coding standards and linting rules (`ruff`).

## License

This project is licensed under the MIT-0 License - see the [LICENSE](LICENSE) file for details.

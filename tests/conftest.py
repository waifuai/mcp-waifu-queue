import pytest
import pytest_asyncio
import fakeredis # Use synchronous fakeredis
import redis # Use synchronous redis for patching if needed
import requests_mock
import unittest.mock
from starlette.testclient import TestClient

# Import the app and config from your project
from mcp_waifu_queue.main import app, config
from mcp_waifu_queue.task_queue import q  # Import the queue instance


@pytest.fixture(scope="session")
def anyio_backend():
    """Use asyncio backend for pytest-asyncio."""
    return "asyncio"


@pytest.fixture(autouse=True)
def mock_rq_imports():
    """
    Mock rq.Queue import within task_queue to avoid Windows signal errors.
    The actual queue 'q' instance will be a MagicMock, but mock_redis
    will correctly patch its 'connection' attribute.
    """
    with unittest.mock.patch('mcp_waifu_queue.task_queue.Queue', new_callable=unittest.mock.MagicMock) as mock_queue:
        # We might need to configure the mock slightly if the tests
        # depend on specific Queue behavior beyond connection setting.
        # For now, a basic MagicMock should suffice as mock_redis handles
        # the connection patching.
        yield mock_queue


# Change to synchronous fixture
@pytest.fixture(scope="function", autouse=True)
def mock_redis(monkeypatch):
    """Replace Redis connection with fakeredis."""
    # Use synchronous FakeRedis
    fake_redis_conn = fakeredis.FakeRedis.from_url(
        config.redis_url
    )

    # Mock the connection used by the queue
    monkeypatch.setattr(q, "connection", fake_redis_conn)

    # Patching redis.from_url might still be needed if task_queue creates its own connection
    # Also patch the 'conn' variable used directly in task_queue.py
    monkeypatch.setattr("mcp_waifu_queue.task_queue.conn", fake_redis_conn)

    # For now, patching q.connection might be sufficient. If not, revisit this.
    # def mock_sync_from_url(*args, **kwargs):
    #     return fake_redis_conn

    # monkeypatch.setattr(redis, "from_url", mock_sync_from_url)

    # Mock the client_list command for SimpleWorker compatibility
    # fakeredis doesn't implement client_list
    def mock_client_list(*args, **kwargs):
        return []
    monkeypatch.setattr(fake_redis_conn, "client_list", mock_client_list)

    yield fake_redis_conn
    fake_redis_conn.flushall() # Use synchronous flushall


@pytest.fixture(scope="function")
def client():
    """Provide a TestClient for the FastMCP app."""
    # Pass the actual Starlette ASGI app instance returned by sse_app()
    with TestClient(app.sse_app()) as client:
        yield client


@pytest.fixture(scope="function")
def mock_requests():
    """Provide a requests_mock instance."""
    with requests_mock.Mocker() as m:
        yield m

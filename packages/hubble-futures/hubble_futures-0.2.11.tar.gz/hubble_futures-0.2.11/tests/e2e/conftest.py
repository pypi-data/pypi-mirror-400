"""Pytest configuration for E2E tests."""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from hubble_futures import ExchangeConfig, create_client
from hubble_futures import clear_function_log, export_function_log, start_function_log


def _mask_value(value: str | None, visible: int = 3) -> str:
    """Mask sensitive value showing only first few chars."""
    if not value or len(value) <= visible + 3:
        return "***"
    return f"{value[:visible]}***{value[-3:]}"


# Load .env file from project root
project_root = Path(__file__).parent.parent.parent
env_file = project_root / ".env"

print(f"\n{'='*60}")
print("E2E Test Configuration Debug:")
print(f"  Project root: {project_root.absolute()}")
print(f"  .env path: {env_file.absolute()}")
print(f"  .env exists: {env_file.exists()}")

if env_file.exists():
    load_dotenv(env_file)
    print("  .env loaded: YES")
    print(f"  RUN_E2E_TESTS: {os.getenv('RUN_E2E_TESTS', 'NOT SET')}")
    print(f"  ASTER_API_KEY: {_mask_value(os.getenv('ASTER_API_KEY'))}")
    print(f"  ASTER_API_SECRET: {_mask_value(os.getenv('ASTER_API_SECRET'))}")
    print(f"  WEEX_API_KEY: {_mask_value(os.getenv('WEEX_API_KEY'))}")
    print(f"  WEEX_API_SECRET: {_mask_value(os.getenv('WEEX_API_SECRET'))}")
    print(f"  WEEX_PASSPHRASE: {_mask_value(os.getenv('WEEX_PASSPHRASE'))}")
    proxy_url = os.getenv('PROXY_URL')
    if proxy_url:
        print(f"  PROXY_URL: {_mask_value(proxy_url, visible=8)}")
        print("  -> Will use PROXY for all connections")
    else:
        print("  PROXY_URL: (not set)")
        print("  -> Will use DIRECT connection (no proxy)")
else:
    print("  .env loaded: NO - file not found!")
print(f"{'='*60}\n")


def should_run_e2e() -> bool:
    """Check if E2E tests should run based on environment variable."""
    return os.getenv("RUN_E2E_TESTS", "false").lower() == "true"


def get_proxy_url() -> str | None:
    """Get proxy URL from environment."""
    proxy = os.getenv("PROXY_URL", "").strip()
    return proxy if proxy else None


@pytest.fixture(scope="session")
def aster_config() -> ExchangeConfig:
    """
    Create Aster exchange configuration from environment variables.
    
    If PROXY_URL is set, all connections will use the proxy.
    If PROXY_URL is not set, all connections will be direct.
    """
    api_key = os.getenv("ASTER_API_KEY")
    api_secret = os.getenv("ASTER_API_SECRET")
    base_url = os.getenv("ASTER_BASE_URL", "https://fapi.asterdex.com")
    proxy_url = get_proxy_url()

    if not api_key or not api_secret:
        pytest.skip("Aster API credentials not configured in .env")

    return ExchangeConfig(
        name="asterdex",
        api_key=api_key,
        api_secret=api_secret,
        base_url=base_url,
        proxy_url=proxy_url
    )


@pytest.fixture(scope="session")
def weex_config() -> ExchangeConfig:
    """
    Create WEEX exchange configuration from environment variables.
    
    If PROXY_URL is set, all connections will use the proxy.
    If PROXY_URL is not set, all connections will be direct.
    """
    api_key = os.getenv("WEEX_API_KEY")
    api_secret = os.getenv("WEEX_API_SECRET")
    passphrase = os.getenv("WEEX_PASSPHRASE")
    base_url = os.getenv("WEEX_BASE_URL", "https://api-contract.weex.com")
    proxy_url = get_proxy_url()

    if not api_key or not api_secret or not passphrase:
        pytest.skip("WEEX API credentials not configured in .env")

    return ExchangeConfig(
        name="weex",
        api_key=api_key,
        api_secret=api_secret,
        passphrase=passphrase,
        base_url=base_url,
        proxy_url=proxy_url
    )


@pytest.fixture(scope="session")
def test_symbol() -> str:
    """Get test symbol from environment or use default."""
    return os.getenv("TEST_SYMBOL", "BTCUSDT")


@pytest.fixture(scope="function")
def aster_client(aster_config):
    """Create Aster client for testing."""
    if not should_run_e2e():
        pytest.skip("E2E tests disabled (set RUN_E2E_TESTS=true in .env to enable)")

    return create_client(aster_config)


@pytest.fixture(scope="function")
def weex_client(weex_config):
    """Create WEEX client for testing."""
    if not should_run_e2e():
        pytest.skip("E2E tests disabled (set RUN_E2E_TESTS=true in .env to enable)")

    return create_client(weex_config)


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers",
        "e2e: End-to-end tests that require real API credentials"
    )


@pytest.fixture(autouse=True)
def function_log_tracker(request):
    """
    Auto-applied fixture that tracks function calls during each test.

    This fixture:
    1. Starts function logging at the beginning of each test
    2. Exports and displays the log at the end of each test
    3. Clears the log for the next test

    The log shows all exchange API calls made during the test,
    including parameters, results, timing, and any errors.
    """
    # Start logging at test beginning
    start_function_log(container_id=f"e2e_test_{request.node.name}")

    # Yield control to the test
    yield

    # After test completes, export and display log
    log = export_function_log(clear=False)

    # Only print if there were actual function calls
    function_calls = log.get("function_calls", [])
    if function_calls:
        print(f"\n{'='*60}")
        print(f"Function Call Log for: {request.node.name}")
        print(f"{'='*60}")

        for call in function_calls:
            func_name = call.get("function", "unknown")
            status = call.get("status", "unknown")
            duration = call.get("duration_ms")

            # Print summary
            status_symbol = "✓" if status == "succeeded" else "✗"
            duration_str = f" ({duration}ms)" if duration else ""
            print(f"{status_symbol} {func_name}{duration_str}")

            # Print parameters (truncated)
            params = call.get("parameters", {})
            if params:
                params_str = str(params)
                if len(params_str) > 60:
                    params_str = params_str[:57] + "..."
                print(f"  Parameters: {params_str}")

            # Print result or error
            if status == "succeeded":
                result = call.get("result", {})
                if result and isinstance(result, dict):
                    # Show key fields from result
                    if "orderId" in result:
                        print(f"  Result: orderId={result['orderId']}")
                    elif "status" in result:
                        print(f"  Result: status={result['status']}")
            else:
                error = call.get("error", "")
                if error:
                    print(f"  Error: {error}")

        print(f"{'='*60}")
        print(f"Total: {len(function_calls)} call(s)")
        print(f"{'='*60}\n")

    # Clear log for next test
    clear_function_log()

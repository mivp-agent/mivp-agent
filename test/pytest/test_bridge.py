import os
import pytest

from mivp_agent.bridge import get_server_host_and_port

@pytest.fixture(autouse=True)
def clear_env_vars_before_and_after():
    os.unsetenv('AGENT_SERVER_HOSTNAME')
    os.unsetenv('AGENT_SERVER_PORT')

    yield

    os.unsetenv('AGENT_SERVER_HOSTNAME')
    os.unsetenv('AGENT_SERVER_PORT')

def test_host_and_port():
    # Test defaults
    host, port = get_server_host_and_port()
    assert host == 'localhost'
    assert port == 57721

    # Test that environment variables are picked up
    os.environ['AGENT_SERVER_HOSTNAME'] = '192.168.1.12'
    os.environ['AGENT_SERVER_PORT'] = '34022'
    host, port = get_server_host_and_port()
    assert host == '192.168.1.12'
    assert port == 34022
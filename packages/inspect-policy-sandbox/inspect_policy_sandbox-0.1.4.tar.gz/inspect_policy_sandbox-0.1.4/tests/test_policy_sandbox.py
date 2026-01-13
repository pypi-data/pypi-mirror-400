import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from inspect_ai.util import SandboxEnvironment, ExecResult
from inspect_policy_sandbox.policy import SandboxPolicy, SandboxPolicyViolationError
from inspect_policy_sandbox.sandbox import PolicySandboxEnvironment

class MockSandbox(SandboxEnvironment):
    async def exec(self, cmd, input=None, cwd=None, env=None, user=None, timeout=None):
        return ExecResult(True, 0, "stdout", "stderr")
    
    async def read_file(self, file, text=True):
        return "content"
    
    async def write_file(self, file, content):
        pass
    
    async def connection(self):
        return "connection"

    @classmethod
    async def sample_cleanup(cls, task_name, config, environments, interrupted):
        pass

@pytest.fixture
def mock_inner():
    return MockSandbox()

@pytest.fixture
def mock_transcript():
    with patch("inspect_policy_sandbox.sandbox.transcript") as mock:
        t_instance = MagicMock()
        mock.return_value = t_instance
        yield t_instance

@pytest.fixture
def policy_sandbox(mock_inner):
    policy = SandboxPolicy(
        deny_exec=["rm"],
        deny_read=["/etc/passwd"],
        deny_write=["/protected/*"]
    )
    env = PolicySandboxEnvironment(inner=mock_inner, policy=policy)
    return env

@pytest.mark.asyncio
async def test_policy_allows_safe_ops(policy_sandbox, mock_transcript):
    await policy_sandbox.exec(["ls", "-l"])
    await policy_sandbox.read_file("valid.txt")
    await policy_sandbox.write_file("output.txt", "data")
    
    # Ensure no policy events were published via info
    # (Actually we use _event, which is internal. Verify _event call if any)
    mock_transcript._event.assert_not_called()

@pytest.mark.asyncio
async def test_policy_blocks_forbidden_exec(policy_sandbox, mock_transcript):
    with pytest.raises(SandboxPolicyViolationError) as excinfo:
        await policy_sandbox.exec(["rm", "-rf", "/"])
    
    assert "Execution of 'rm' is denied" in str(excinfo.value)
    
    # Verify event emission
    mock_transcript._event.assert_called_once()
    event = mock_transcript._event.call_args[0][0]
    assert event.result == 1
    assert event.metadata["reason"] == "policy"
    assert event.metadata["command"] == "rm"

@pytest.mark.asyncio
async def test_policy_blocks_forbidden_read(policy_sandbox, mock_transcript):
    with pytest.raises(SandboxPolicyViolationError):
        await policy_sandbox.read_file("/etc/passwd")

    mock_transcript._event.assert_called_once()
    event = mock_transcript._event.call_args[0][0]
    assert event.metadata["file"] == "/etc/passwd"
    assert event.metadata["policy"] == "read_file"

@pytest.mark.asyncio
async def test_policy_blocks_forbidden_write(policy_sandbox, mock_transcript):
    with pytest.raises(SandboxPolicyViolationError):
        await policy_sandbox.write_file("/protected/config.json", "hack")

    mock_transcript._event.assert_called_once()
    event = mock_transcript._event.call_args[0][0]
    assert event.metadata["file"] == "/protected/config.json"
    assert event.metadata["policy"] == "write_file"

@pytest.mark.asyncio
async def test_delegation(policy_sandbox, mock_inner):
    # Test as_type delegation
    assert policy_sandbox.as_type(MockSandbox) == mock_inner
    assert policy_sandbox.as_type(PolicySandboxEnvironment) == policy_sandbox
    
    # Test connection delegation
    conn = await policy_sandbox.connection()
    assert conn == "connection"

@pytest.mark.asyncio
async def test_allow_list_logic(mock_transcript):
    # Test that allow list implies deny all fail-close
    policy = SandboxPolicy(allow_exec=["ls"])
    mock = MockSandbox()
    env = PolicySandboxEnvironment(inner=mock, policy=policy)

    # Allowed
    await env.exec(["ls"])
    
    # Blocked (not in allow list)
    with pytest.raises(SandboxPolicyViolationError):
        await env.exec(["cat", "file"])
        
    mock_transcript._event.assert_called()

from datetime import datetime
import shlex
import fnmatch
from typing import Any, Dict, List, Literal, Optional, Union, overload

from inspect_ai.util import SandboxEnvironment, SandboxConnection, ExecResult, sandboxenv
from inspect_ai.event import SandboxEvent
from inspect_ai.event import SandboxEvent
from inspect_ai.log import transcript
from inspect_ai.util._sandbox.registry import registry_find_sandboxenv

from .policy import SandboxPolicy, SandboxPolicyViolationError

@sandboxenv(name="policy-sandbox")
class PolicySandboxEnvironment(SandboxEnvironment):
    """Sandbox environment that enforces a policy on a wrapped sandbox."""

    def __init__(self, inner: SandboxEnvironment, policy: SandboxPolicy):
        super().__init__()
        self._inner = inner
        self._policy = policy

    async def exec(
        self,
        cmd: list[str],
        input: str | bytes | None = None,
        cwd: str | None = None,
        env: dict[str, str] = {},
        user: str | None = None,
        timeout: int | None = None,
        **kwargs: Any,
    ) -> ExecResult:
        # Check Policy
        command_str = cmd[0] if cmd else ""
        
        allowed = True
        
        if self._policy.deny_exec:
             for pattern in self._policy.deny_exec:
                 if fnmatch.fnmatch(command_str, pattern):
                     allowed = False
                     break
        
        if allowed and self._policy.allow_exec:
            allowed = False
            for pattern in self._policy.allow_exec:
                 if fnmatch.fnmatch(command_str, pattern):
                     allowed = True
                     break
        
        if not allowed:
            metadata = {
                "command": command_str,
                "policy": "exec",
                "reason": "policy"
            }
            transcript()._event(SandboxEvent(
                action="exec",
                cmd=command_str,
                result=1,
                metadata=metadata,
                timestamp=datetime.now()
            ))
            raise SandboxPolicyViolationError(f"Execution of '{command_str}' is denied by policy.")

        return await self._inner.exec(cmd, input, cwd, env, user, timeout, **kwargs)

    async def read_file(self, file: str, text: bool = True, **kwargs: Any) -> Union[str, bytes]:
        # Check Policy
        allowed = True
        if self._policy.deny_read:
             for pattern in self._policy.deny_read:
                 if fnmatch.fnmatch(file, pattern):
                     allowed = False
                     break
        
        if allowed and self._policy.allow_read:
            allowed = False
            for pattern in self._policy.allow_read:
                 if fnmatch.fnmatch(file, pattern):
                     allowed = True
                     break

        if not allowed:
            metadata = {
                "file": file,
                "policy": "read_file",
                "reason": "policy"
            }
            transcript()._event(SandboxEvent(
                action="read_file",
                file=file,
                result=1,
                metadata=metadata,
                timestamp=datetime.now()
            ))
            raise SandboxPolicyViolationError(f"Reading file '{file}' is denied by policy.")
            
        return await self._inner.read_file(file, text, **kwargs)

    async def write_file(self, file: str, content: Union[str, bytes], **kwargs: Any) -> None:
        # Check Policy
        allowed = True
        if self._policy.deny_write:
             for pattern in self._policy.deny_write:
                 if fnmatch.fnmatch(file, pattern):
                     allowed = False
                     break
        
        if allowed and self._policy.allow_write:
            allowed = False
            for pattern in self._policy.allow_write:
                 if fnmatch.fnmatch(file, pattern):
                     allowed = True
                     break

        if not allowed:
            metadata = {
                "file": file,
                "policy": "write_file",
                "reason": "policy"
            }
            transcript()._event(SandboxEvent(
                action="write_file",
                file=file,
                result=1,
                metadata=metadata,
                timestamp=datetime.now()
            ))
            raise SandboxPolicyViolationError(f"Writing to file '{file}' is denied by policy.")

        await self._inner.write_file(file, content, **kwargs)

    async def connection(self) -> SandboxConnection:
        return await self._inner.connection()
        
    def as_type(self, type: type[Any]) -> Any | None:
        # Delegate to inner if not self
        if isinstance(self, type):
            return self
        return self._inner.as_type(type)
    
    @classmethod
    async def sample_cleanup(cls, task_name: str, config: Any, environments: Dict[str, "SandboxEnvironment"], interrupted: bool) -> None:
        # NO-OP as per requirements. 
        pass

    @classmethod
    async def sample_init(cls, task_name: str, config: Any, metadata: Dict[str, Any]) -> Dict[str, SandboxEnvironment]:
        # Extract policy config from metadata
        policy_config = metadata.get("policy", {})
        policy = SandboxPolicy(
            allow_exec=policy_config.get("allow_exec", []),
            deny_exec=policy_config.get("deny_exec", []),
            allow_read=policy_config.get("allow_read", []),
            deny_read=policy_config.get("deny_read", []),
            allow_write=policy_config.get("allow_write", []),
            deny_write=policy_config.get("deny_write", [])
        )

        # Resolve inner sandbox
        inner_sandbox_name = metadata.get("inner_sandbox", "local")
        sandbox_cls = registry_find_sandboxenv(inner_sandbox_name)

        # Instantiate inner sandbox
        # Note: We support inner sandboxes that use sample_init (like Docker)
        # or simple init (like Local).
        if hasattr(sandbox_cls, "sample_init"):
            inner_result = await sandbox_cls.sample_init(task_name, config, metadata)
            if isinstance(inner_result, dict):
                inner = inner_result.get("default")
                if not inner:
                    # Fallback if no default, take the first one or error
                    # For safety, strict assumption: inner sandbox sample_init returns properly
                    inner = next(iter(inner_result.values()))
            else:
                inner = inner_result
        else:
            inner = sandbox_cls()

        return {"default": cls(inner, policy)}

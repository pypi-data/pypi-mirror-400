# Inspect Policy Sandbox Extension

A standalone extension for [Inspect AI](https://github.com/UKGovernmentBEIS/inspect_ai) that provides a policy-enforced sandbox environment.

## Overview

The `inspect-policy-sandbox` extension allows you to wrap any existing Inspect sandbox environment (e.g., `local`, `docker`) and enforce strict policies on:

- **Execution**: Allow or deny specific commands.
- **Read Access**: Allow or deny reading specific files.
- **Write Access**: Allow or deny writing to specific files.

When a policy violation occurs, the extension:
1. Raises a `SandboxPolicyViolationError` (subclass of `PermissionError`).
2. Logs a `SandboxEvent` with `result=1` and `reason="policy"`.

## Installation

### Install from PyPI (recommended)

```bash
pip install inspect-policy-sandbox
```

## Usage

Enable the extension in your Inspect task by specifying the sandbox type as `policy-sandbox`.

You can configure the policy via task metadata or configuration.

### Example Task

```python
from inspect_ai import Task, eval
from inspect_ai.dataset import FieldSpec
from inspect_ai.solver import system_message

# Define task using the policy sandbox
task = Task(
    dataset=[], 
    solver=[system_message("Run a command")],
    sandbox="policy-sandbox",
    sandbox_config={
        # Configuration for the inner sandbox (if needed)
    }
)

# Pass policy configuration in metadata at runtime or task definition
# Note: Currently policy configuration is extracted from sample metadata or task metadata 
# depending on how you pass it. The extension looks for a 'policy' dictionary in metadata.
```

### Policy Configuration

The policy is defined by a dictionary with the following keys:

- `deny_exec`: List of glob patterns for commands to deny (e.g., `["rm", "sudo"]`).
- `allow_exec`: List of glob patterns for commands to allow (whitelist).
- `deny_read`: List of glob patterns for files to deny reading.
- `allow_read`: List of glob patterns for files to allow reading.
- `deny_write`: List of glob patterns for files to deny writing.
- `allow_write`: List of glob patterns for files to allow writing.

Example Metadata:
```json
{
  "policy": {
    "deny_exec": ["rm", "curl"],
    "deny_write": ["/etc/*"]
  },
  "inner_sandbox": "local"
}
```


# qBraid Core Development

> **MIGRATION IN PROGRESS:** Part of the Environment Manager Migration.
> Before changing `qbraid_core/services/environments/`, read:
> - `../migration/PROGRESS.md` - Current status and tasks
> - `../migration/INTERFACES.md` - API contracts
>
> **Branch:** `enhancing_envs`

## Structure

```
qbraid_core/
├── services/
│   ├── environments/  # EnvironmentManagerClient, EnvironmentRegistryManager
│   ├── quantum/       # Quantum job submission
│   ├── mcp/           # MCP WebSocket client
│   └── ...
├── system/            # Executables, packages, versions
└── sessions.py        # QbraidSession
tests/                 # Mirrors source structure
```

## Commands

```bash
# Testing
tox -e unit-tests          # Run tests with coverage (target: 80%)
pytest tests/environments/ # Run specific tests

# Linting
tox -e format-check        # Check all linters
tox -e linters             # Auto-fix formatting

# Install for dev
pip install -e ".[test,environments,mcp]"
```

## Key Files for Environments

- `services/environments/client.py` - EnvironmentManagerClient (API calls)
- `services/environments/registry.py` - EnvironmentRegistryManager (local registry)
- `services/environments/schema.py` - EnvironmentConfig, EnvironmentEntry models
- `services/environments/exceptions.py` - Custom exceptions

## Testing Notes

- Use `pytest.mark.asyncio` for async tests
- Mock external calls with `unittest.mock` or `monkeypatch`
- See existing tests in `tests/environments/` for patterns

## Environment Variable for Local API Testing

```bash
QBRAID_API_URL="http://localhost:3001/api/v1" python script.py
```

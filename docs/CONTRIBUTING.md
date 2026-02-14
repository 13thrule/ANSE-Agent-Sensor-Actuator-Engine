# Contributing to ANSE

Thank you for your interest in contributing to ANSE!

## Development Setup

1. Fork and clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   pip install -e .
   ```

## Code Style

- Follow PEP 8
- Use `black` for formatting: `black anse/ tests/`
- Use type hints where appropriate
- Write docstrings for all public functions

## Adding New Tools

1. Create tool function in `anse/tools/`:
   ```python
   async def my_tool(param: str) -> Dict[str, Any]:
       """Tool description."""
       # Implementation
       return {"result": ...}
   ```

2. Register in `engine_core.py`:
   ```python
   self.tools.register(
       name="my_tool",
       func=my_tool,
       schema={...},
       description="...",
       sensitivity="low",
       cost_hint={...}
   )
   ```

3. Add tests in `tests/test_tools.py`
4. Update documentation in `docs/API.md`

## Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_tools.py -v

# With coverage
pytest tests/ --cov=anse --cov-report=html
```

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Run tests: `pytest tests/`
4. Run linter: `black anse/ tests/`
5. Update documentation if needed
6. Commit with descriptive message
7. Push and create PR

## Tool Design Guidelines

- **Async by default** - All tools must be async functions
- **Graceful errors** - Return error dicts, don't raise exceptions
- **Validate inputs** - Check parameters before execution
- **Document outputs** - Clear docstrings and return types
- **Consider cost** - Include latency and resource hints

## Safety Considerations

When adding tools, consider:
- **Permission scope** - What access level is required?
- **Rate limiting** - How fast can this be called safely?
- **Data retention** - What data is stored and for how long?
- **Risk level** - Could this be abused? Does it need approval?

Update `safety_policy.yaml` accordingly.

## Documentation

- Update `docs/API.md` for new tools
- Update `docs/DESIGN.md` for architectural changes
- Keep `README.md` and `QUICKSTART.md` current
- Add examples for complex features

## Questions?

Open an issue for discussion before major changes.

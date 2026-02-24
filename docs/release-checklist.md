# Release Checklist

1. Confirm test suite passes:
   - `python -m pytest`
2. Confirm integration smoke checks pass:
   - `python scripts/smoke_integrations.py`
3. Confirm docs are updated:
   - `README.md`
   - `docs/integrations.md`
4. Confirm version and schema values:
   - package version in `pyproject.toml`
   - `SCHEMA_VERSION` in `src/llm_prep/__init__.py`
5. Build package:
   - `python -m pip install build`
   - `python -m build`
6. Publish to PyPI:
   - `python -m pip install twine`
   - `python -m twine upload dist/*`

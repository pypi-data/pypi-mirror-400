            uv pip install build
          uv run python -m build
          uv pip install twine
          uv run twine upload dist/* -u __token__ -p $PYPI_TOKEN


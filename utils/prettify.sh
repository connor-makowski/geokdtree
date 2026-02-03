#!/bin/bash
cd /app/
# Lint and Autoformat the code in place
# Remove unused imports
autoflake --in-place --remove-all-unused-imports --ignore-init-module-imports -r ./geokdtree --exclude=core.py
# Perform all other steps
black --config pyproject.toml ./geokdtree
black --config pyproject.toml ./test

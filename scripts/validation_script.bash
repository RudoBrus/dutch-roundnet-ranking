#!/bin/bash

set -e

# Set the absolute path to the project root
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TARGET_FOLDERS="$PROJECT_ROOT/ranking_calculator $PROJECT_ROOT/tests"

echo "Running mypy..."
pipenv run mypy $TARGET_FOLDERS

echo "Running pylint..."
pipenv run pylint $TARGET_FOLDERS

echo "Running ruff..."
pipenv run ruff format --check $TARGET_FOLDERS
pipenv run ruff check $TARGET_FOLDERS

echo "Running pytest..."
pipenv run pytest $PROJECT_ROOT/tests

echo "All checks passed successfully!"
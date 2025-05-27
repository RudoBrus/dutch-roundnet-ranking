#!/bin/bash

SCRIPT_DIR=$(dirname "$(realpath "$0")")
pipenv run python "$SCRIPT_DIR/../ranking_calculator" --categories beginner
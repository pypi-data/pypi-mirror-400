#!/bin/bash
set -e
pip install --quiet --requirement requirements.txt
mypy *.py tests/*.py
pylint "*.py" "tests/*.py"
coverage run -m pytest
coverage report -m
rm -f dist/*
python -m build

#!/bin/bash
set -e
export PYTHON_VERSION=3.11
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
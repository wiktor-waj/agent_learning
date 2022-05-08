#!/usr/bin/env sh

set -e

# Try virtualenv first, then venv, if all fails bail out due to "set -e"
if ! python3 -m virtualenv -p python3 venv; then
    python3 -m venv venv
fi

# Activate the virtualenv
. venv/bin/activate

# Install dependencies
pip install -r requirements.txt

#!/bin/bash

# Check if at least two arguments are provided (path and at least one module)
if [ "$#" -lt 2 ]; then
  echo "Usage: $0 PATH MODULE1 [MODULE2 ...]"
  exit 1
fi

# The first argument is the path to create the virtual environment in
VENV_PATH="$1"
shift  # Shift arguments to the left, so $@ contains only the module names

# Create a Python virtual environment at the specified path
python3 -m venv "$VENV_PATH" || { echo "Failed to create a virtual environment at $VENV_PATH"; exit 1; }

# Activate the virtual environment
source "$VENV_PATH/bin/activate" || { echo "Failed to activate the virtual environment at $VENV_PATH"; exit 1; }

# Upgrade pip to the latest version
pip install --upgrade pip

# Install the modules passed as arguments
for module in "$@"; do
  pip install "$module" || { echo "Failed to install module $module"; exit 1; }
done

echo "All modules installed successfully."

# Optionally, deactivate the virtual environment
# deactivate

exit 0
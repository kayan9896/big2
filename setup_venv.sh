#!/bin/bash

# Check if the path and module names are provided
if [ $# -lt 2 ]; then
  echo "Usage: $0 <path> <module1> [module2] [module3] ..."
  exit 1
fi

# Get the path and module names
VENV_PATH=$1
MODULES=${@:2}

# Create the virtual environment
python -m venv $VENV_PATH

# Activate the virtual environment
source $VENV_PATH/bin/activate

# Install the modules
pip install $MODULES

# Deactivate the virtual environment
deactivate
              
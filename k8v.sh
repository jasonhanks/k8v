#!/bin/bash


# navigate to the project root folder
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR


# Load the virtualenv if it exists
[ -d "$SCRIPT_DIR/.env" ] && source $SCRIPT_DIR/.env/bin/activate


# Run the application interface
python3 app.py "$@"

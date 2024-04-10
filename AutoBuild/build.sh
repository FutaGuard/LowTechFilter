#!/bin/bash

# Get the first argument
arg=$1

# Check the argument value
if [ "$arg" == "build" ]; then
    pip install -r AutoBuild/requirements.txt && python AutoBuild/builder.py
elif [ "$arg" == "nrdlist" ]; then
    pip install -r AutoBuild/requirements.txt && python AutoBuild/nrdlist.py
else
    echo "Invalid argument. Please use 'build' or 'nrdlist'."
fi
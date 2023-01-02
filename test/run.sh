#!/usr/bin/env bash

# CD to directory of this executable to allow relative paths
PREVIOUS_WD="$(pwd)"
DIRNAME="$(dirname $0)"
cd $DIRNAME

# Restore dir when done
function restore_cwd {
    cd $PREVIOUS_WD
}
trap restore_cwd EXIT

set -e # Exit if anything fails, important for GH runners to have correct error code
if [[ "$1" == "--integration" ]]; then
  pytest integration
elif [[ "$1" == "" ]]; then
  cd unittest && ./test_all.py
  cd ..

  cd pytests && python3 -m pytest .
  cd ..
else
  echo "Usage: $0 [--integration]"
fi

cd $PREVIOUS_WD
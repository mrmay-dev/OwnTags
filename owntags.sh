#!/bin/bash
# https://linuxconfig.org/how-to-use-a-bash-script-to-run-your-python-scripts

echo
echo "-- START SCRIPT --"
# Directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Defaults: Directory for the virtual environment
VENV_DIR="$SCRIPT_DIR/venv"
source "$VENV_DIR/bin/activate"
wait

cd "$SCRIPT_DIR"
python3 request_reports.py --prefix $1 --owntracks
echo "-- End Script --"
echo

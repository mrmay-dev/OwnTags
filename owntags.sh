#!/bin/bash
# https://linuxconfig.org/how-to-use-a-bash-script-to-run-your-python-scripts

# Directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Defaults: Directory for the virtual environment
VENV_DIR="$SCRIPT_DIR/venv"
source "$VENV_DIR/bin/activate"
wait

cd "$SCRIPT_DIR/application"
# time should be entered as hh:mm if hardcoded here

# use this to run the proxy/client method
# python3 FindMy_client.py --time $1 --owntags

# use this for the standalone method
# python3 request_reports.py --time $1
# python3 request_reports.py --time $1 --prefix $2
python3 request_reports.py --time $1 --owntags

echo "-- END SCRIPT --"

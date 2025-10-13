#!/bin/sh
echo "Chaasnyx installer"
python3 -m venv venv
echo "Created venv"
source venv/bin/activate
echo "Activated"
pip install websockets
pip install prompt_toolkit
echo "Installed"

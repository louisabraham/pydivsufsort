#!/bin/sh

echo "y" |  python -m pip uninstall pydivsufsort
python -m pip install -r requirements.txt
python -m pip install pydivsufsort

#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Run Django development server
python3 manage.py runserver

# Deactivate virtual environment on exit
deactivate 
#!/usr/bin/env bash
source luncho_pyenv/bin/activate
# source luncho_pypyenv/bin/activate
gunicorn --access-logfile - --error-logfile - -k uvicorn.workers.UvicornH11Worker -c gunicorn_config.py main:app --reload --timeout 600

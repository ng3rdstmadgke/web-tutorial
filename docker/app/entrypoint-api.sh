#!/bin/bash
cd /opt/app/api
printenv
uvicorn main:app --reload --port 8018 --host 0.0.0.0
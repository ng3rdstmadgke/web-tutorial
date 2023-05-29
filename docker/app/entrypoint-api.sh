#!/bin/bash
cd /opt/app
printenv
uvicorn main:app --reload --port 8018
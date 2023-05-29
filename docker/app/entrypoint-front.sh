#!/bin/bash
FRONT_DIR=/opt/app/front
if [ -d "$FRONT_DIR" ]; then
  cd $FRONT_DIR
  npm install
  npm run dev
fi
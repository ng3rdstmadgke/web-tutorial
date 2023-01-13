#!/bin/bash

for i in $(seq 1 30); do
  success=$(MYSQL_PWD=$DB_PASSWORD mysql -u $DB_USER -h $DB_HOST -P $DB_PORT -e "SELECT 'success'" >/dev/null 2>&1; echo $?)
  if [ "$success" = "0" ]; then
    echo "success!!"
    exit
  else
    echo "mysql booting..."
  fi
  sleep 1
done
echo "failed..."
exit 1
#!/bin/bash

OUTPUT="$(createdb recipes 2>&1)"
RESULT=$?
if [[ $RESULT -eq 0 || $OUTPUT == *"already exists"* ]]; then
    echo "DB Created"
else
    echo $OUTPUT
    exit 1
fi

cd /opt/app/migrations
alembic upgrade head
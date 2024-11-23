#!/bin/bash

pip install -r /app/tests/functional/requirements.txt
python3 /app/tests/functional/utils/wait_for_es.py
python3 /app/tests/functional/utils/wait_for_redis.py
pytest /app/tests/functional/src

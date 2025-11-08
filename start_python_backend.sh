#!/bin/bash
cd "$(dirname "$0")"
PORT=${PORT:-8001}
uvicorn python_backend.main:app --host 0.0.0.0 --port $PORT --reload

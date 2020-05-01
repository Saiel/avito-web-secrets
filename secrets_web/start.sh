#!/bin/sh
python -m aiohttp.web src.app:init_app -H 0.0.0.0 -P 8000 -U /run/sockets/secret_service_1s.sock
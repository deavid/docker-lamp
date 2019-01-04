#!/bin/bash
test -f config.sh && source config.sh
export SCRIPT_NAME=container-admin.py
export FLASK_DEBUG=1
uwsgi -p4 --lazy-apps --uwsgi-socket 0.0.0.0:3031 -i \
  --uid 33 --gid 33 \
  --manage-script-name --py-autoreload 1 --mount /=container-admin:app

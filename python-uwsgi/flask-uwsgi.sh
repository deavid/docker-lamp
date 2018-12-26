#!/bin/bash
test -f config.sh && source config.sh
export SCRIPT_NAME=appname/__init__.py

# export FLASK_DEBUG=1
# uwsgi --http :9090 --wsgi-file foobar.py
# uwsgi -p8 --lazy-apps --uwsgi-socket 0.0.0.0:3031 -i --manage-script-name --mount /=appname:app --py-autoreload 1
uwsgi -p8 --lazy-apps --uwsgi-socket 0.0.0.0:3031 -i \
  --manage-script-name --py-autoreload 1 --wsgi-file foobar.py

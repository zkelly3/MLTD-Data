#!/usr/bin/env bash
trap "pkill -TERM -P $$" EXIT
while inotifywait -e close_write -r static templates frontend/src; do
    npm run build --prefix frontend
    uwsgi --reload uwsgi.pid
done

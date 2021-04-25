#!/usr/bin/env bash
trap "pkill -TERM -P $$" EXIT
while inotifywait -e close_write -r static templates frontend/dist; do
    uwsgi --reload uwsgi.pid
done

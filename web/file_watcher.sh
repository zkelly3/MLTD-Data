#!/usr/bin/env bash
trap "pkill -TERM -P $$" EXIT
while inotifywait -e close_write -r static templates; do
    uwsgi --reload uwsgi.pid
done

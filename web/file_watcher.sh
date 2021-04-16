#!/usr/bin/env bash
while inotifywait -e close_write -r static templates; do
    uwsgi --reload uwsgi.pid
done

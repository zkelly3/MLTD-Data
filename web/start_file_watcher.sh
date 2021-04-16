#!/usr/bin/env bash
daemonize -a -o log/file_watcher.log -e log/file_watcher.error.log -p file_watcher.pid -l file_watcher.lock -c `pwd` `pwd`/file_watcher.sh

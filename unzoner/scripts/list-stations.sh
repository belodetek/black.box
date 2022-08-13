#!/usr/bin/env bash

[ -e "/root/functions" ] && . /root/functions
[ -e "/dev/shm/.env" ] && . /dev/shm/.env

if [[ "${DEBUG}" == "1" ]]; then
    env
fi

stations=0

if [[ $(get_wiface) ]]; then
    if [[ $(which iw) ]]; then
        stations=$(iw dev $(get_wiface) station dump | grep Station | wc -l)
    fi
fi

printf "${stations}"

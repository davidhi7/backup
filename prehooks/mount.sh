#!/usr/bin/env bash

source $CONFIG
mountpoint -q $REPOSITORY
if [ $? -eq 0 ]; then
    echo '=> Repository is already mounted'
else
    echo '=> Mounting repository'
    mount $REPOSITORY
    if [ $? -ne 0 ]; then
        echo "=> ERROR while mounting repository, exit value = $?" >&2
        exit 1
    fi
fi
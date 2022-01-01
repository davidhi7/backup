#!/usr/bin/env bash

source $CONFIG
echo '=> Unmounting repository'
umount $REPOSITORY
if [ $? -ne 0 ]; then
    echo "=> ERROR while unmounting repository, exit value = $?" >&2
fi
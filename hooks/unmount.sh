#!/usr/bin/env bash

echo '> Executing unmount prehook'
umount $REPOSITORY
if [ $? -ne 0 ]; then
    echo "> ERROR while unmounting repository, exit value = $?" >&2
fi

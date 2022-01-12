#!/usr/bin/env bash

source /etc/backup/hooks/rclone.conf
echo '> Executing rclone sync prehook'
borg with-lock $REPOSITORY rclone sync $REPOSITORY $REMOTE

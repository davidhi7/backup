#!/usr/bin/env bash

source $CONFIG
source /etc/backup/hooks/rclone.conf
echo '=> starting to clone repository'
borg with-lock $REPOSITORY rclone sync $REPOSITORY $REMOTE
echo '=> finished cloning repository'
#!/usr/bin/env bash

echo '> Executing Debian prehook'
apt-get clean
dpkg -l  > backup-apt-installed.list
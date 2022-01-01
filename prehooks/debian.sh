#!/usr/bin/env bash

echo '=> Clearing APT package cache'
apt-get clean

echo '=> Creating list of all installed packages'
dpkg -l  > backup-apt-installed.list
if [ -x "$(command -v flatpak)" ]; then
    flatpak list > backup-flatpak.list
fi
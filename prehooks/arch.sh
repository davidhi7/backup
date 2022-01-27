#!/usr/bin/env bash

echo '> Executing Arch prehook'
paccache -r
pacman -Qq  > backup-pacman-installed.list
pacman -Qqe > backup-pacman-explicit.list
pacman -Qqm > backup-pacman-foreign.list

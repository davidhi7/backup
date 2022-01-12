#!/usr/bin/env bash

echo '> Executing OpenSUSE prehook'
zypper clean
zypper purge-kernels
zypper search --installed-only  > backup-zypper-installed.list

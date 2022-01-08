#!/usr/bin/env bash

zypper clean
zypper purge-kernels
zypper search --installed-only  > backup-zypper-installed.list

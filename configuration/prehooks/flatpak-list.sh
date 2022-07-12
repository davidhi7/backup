#!/usr/bin/env bash

echo '> Executing Flatpak prehook'
flatpak list > backup-flatpak.list

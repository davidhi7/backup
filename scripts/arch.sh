echo '=> Clearing pacman package cache'
paccache -r

echo '=> Creating list of all installed packages'
pacman -Qq  > backup-pacman-all.list
pacman -Qqe > backup-pacman-explicit.list
pacman -Qqm > backup-pacman-foreign.list
if [ -x "$(command -v flatpak)" ]; then
    flatpak list > backup-flatpak.list
fi
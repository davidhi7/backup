echo '=> Clearing APT package cache'
apt-get clean

echo '=> Creating list of all installed packages'
ap-get list --installed  > backup-apt-installed.list
if [ -x "$(command -v flatpak)" ]; then
    flatpak list > backup-flatpak.list
fi
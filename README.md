# Simple wrapper for Borg
This minimal wrapper allows easy configuration and hook configuration as well as ismple Discord webhook integration in case of errors during the backup process.

Creating a new repository is outside the scope of this wrapper. It must be done manually using `borg init`.

## Requirements
* Python 3
* Borg
* Curl (for Discord webhook)

## Installation
`install.sh` provides a poor installation script which moves all the files to their intented path. Run it as root: `chmod +x install.sh; sudo ./install.sh`

Enable the backup using `systemctl enable --now backup.timer`

## Configuration
* `/etc/backup/backup.conf`: main configuration
* `/etc/backup/discord.conf`: Discord webhook configuration
* `/etc/systemd/system/backup.timer`: systemd timer configuration. For the syntax, see https://wiki.archlinux.org/title/Systemd/Timers.

## Usage
* Run the backup routine: `backup create`
* Interact with the repository: `backup exec <command>`, this allows to perform various Borg commands on the repository such as `borg extract` to recover from the backup without needing to manually provide the repository path and passphrase.

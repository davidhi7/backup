# Simple wrapper for Borg
This minimal wrapper allows easy configuration and hook configuration as well as simple Discord webhook integration in case of errors during the backup process.

Creating a new repository is outside the scope of this wrapper. It must be done manually using `borg init`.

## Requirements
* Python 3
* Borg
* curl (for notifications via either Discord webhooks or ntfy notifications)

## Installation
`install.sh` provides a simple installation script which moves all the files to their intented path and does some basic configuration. Run it as root: `$ chmod +x install.sh && sudo ./install.sh`

Enable the backup scheduling using `systemctl enable --now backup.timer`

## Configuration
* `/etc/backup/backup.conf`: Main configuration
* `/etc/backup/exclude.conf`: List of files and dictionaries to be excluded from the backup. See https://borgbackup.readthedocs.io/en/stable/usage/create.html
* `/etc/systemd/system/backup.timer`: Systemd timer configuration. Editing this file allows for configuration of the backup scheduling. For the syntax, see https://wiki.archlinux.org/title/Systemd/Timers. Note that for the changes to be applied, you need to run `# systemctl daemon-reload && systemctl restart backup.timer`

## Usage
* Run the backup routine: `backup create`.
* Interact with the repository: `backup exec <command>`. This allows to perform various Borg commands on the repository such as `borg extract` to recover from the backup without the need to provide the repository path and passphrase manually.

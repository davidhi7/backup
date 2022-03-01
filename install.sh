#!/usr/bin/env bash

CONFIG_DIR=/etc/backup/
BIN_DIR=/usr/local/bin/
SYSTEMD_DIR=/etc/systemd/system/

if [[ -d $CONFIG_DIR && "$(ls -A $CONFIG_DIR)" ]]; then
    echo "moving old contents of directory $CONFIG_DIR into $CONFIG_DIR/etc-backup/. Merge new and old configuration files manually if required."
    echo "Backup will be overriden during the next installation using this script."
    cd $CONFIG_DIR
    [[ -d etc-backup ]] || mkdir etc-backup/
    find . -mindepth 1 -maxdepth 1 -not -name etc-backup -exec bash -c "cp -r {} etc-backup/ && rm -r {}" \;
    cd - > /dev/null
fi

mkdir -p $CONFIG_DIR $CONFIG_DIR/secrets $BIN_DIR

# TODO: ask before overwrite
cp *.conf $CONFIG_DIR
cp -r hooks/ prehooks/ $CONFIG_DIR
chmod -R +x $CONFIG_DIR/{hooks,prehooks}/

cp systemd/* $SYSTEMD_DIR/

cp notify-discord $BIN_DIR/notify-discord
cp backup.py $BIN_DIR/backup
chmod +x $BIN_DIR/{backup,notify-discord}

read -p 'repository passphrase: ' PASSPHRASE
read -p 'webhook url: ' WEBHOOK
umask 177
echo $PASSPHRASE > $CONFIG_DIR/secrets/passphrase.secret
echo $WEBHOOK > $CONFIG_DIR/secrets/webhook.secret

systemctl enable --now backup.timer

echo 'You should soon receive a confirmation message in Discord!'
$BIN_DIR/notify-discord 'meta:confirmation'

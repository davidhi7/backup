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

# TODO: ask before overwriting
cp -r configuration/* $CONFIG_DIR
chmod -R +x $CONFIG_DIR/{hooks,prehooks}/

cp systemd/* $SYSTEMD_DIR/

cp notifications/* $BIN_DIR/
cp backup.py $BIN_DIR/
chmod +x $BIN_DIR/{backup,notify-*}

umask 177
read -p 'Do you want to use ntfy (Default) or Discord Webhooks for notifications? [N/d] ' NOTIFICATION_SERVICE

if [[ "$NOTIFICATION_SERVICE" = "d" || "$NOTIFICATION_SERVICE" = "D" ]]; then
read -p 'Enter your Discord webhook url: ' WEBHOOK
echo $WEBHOOK > $CONFIG_DIR/secrets/webhook.secret
sed -i 's/ExecStart=notify-ntfy/ExecStart=notify-discord/' $SYSTEMD_DIR/backup-notification@.service
else
read -p 'Enter your ntfy topic url (e.g. https://ntfy.sh/my-backup): ' NTFY_TOPIC
echo $NTFY_TOPIC > $CONFIG_DIR/secrets/ntfy-url.secret
fi

read -p 'Enter your repository passphrase: ' PASSPHRASE
echo $PASSPHRASE > $CONFIG_DIR/secrets/passphrase.secret

echo 'You should now receive a confirmation message via your selected notification service!'
echo 'Enable the backup scheduling by executing the command "systemctl enable --now backup.timer"'
systemctl daemon-reload
systemctl start backup-notification@:confirm_installation:

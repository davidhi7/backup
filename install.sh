CONFIG_DIR=/etc/backup/
BIN_DIR=/usr/local/bin/
SYSTEMD_DIR=/etc/systemd/system/

mkdir -p $CONFIG_DIR $CONFIG_DIR/secrets $BIN_DIR

cp -n *.conf $CONFIG_DIR
cp -nr scripts/ $CONFIG_DIR
cp {backup,notify-discord} $BIN_DIR
cp systemd/* $SYSTEMD_DIR/

systemctl enable --now backup.timer

chmod +x $BIN_DIR/{backup,notify-discord}

read -p 'repository passphrase: ' PASSPHRASE
echo $PASSPHRASE > $CONFIG_DIR/secrets/passphrase.secret

read -p 'webhook url: ' WEBHOOK
echo $WEBHOOK > $CONFIG_DIR/secrets/webhook.secret

$BIN_DIR/notify-discord backup.service

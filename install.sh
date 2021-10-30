CONFIG_DIR=/etc/backup/
BIN_DIR=/usr/local/bin/
SYSTEMD_DIR=/etc/systemd/system/

mkdir -p $CONFIG_DIR $CONFIG_DIR/secrets $BIN_DIR
chmod 600 $CONFIG_DIR/secrets

cp -n  *.conf $CONFIG_DIR
cp -nr scripts/ $CONFIG_DIR
cp -n  systemd/* $SYSTEMD_DIR/

cp {backup,notify-discord} $BIN_DIR
chmod +x $BIN_DIR/{backup,notify-discord}

read -p 'repository passphrase: ' PASSPHRASE
read -p 'webhook url: ' WEBHOOK
echo $PASSPHRASE > $CONFIG_DIR/secrets/passphrase.secret
echo $WEBHOOK > $CONFIG_DIR/secrets/webhook.secret

systemctl enable --now backup.timer

echo 'You should soon receive a confirmation message in Discord!'
$BIN_DIR/notify-discord 'meta:confirmation'

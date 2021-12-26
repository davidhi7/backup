CONFIG_DIR=/etc/backup/
BIN_DIR=/usr/local/bin/
SYSTEMD_DIR=/etc/systemd/system/

if [[ -d $CONFIG_DIR && "$(ls -A $CONFIG_DIR)" ]]; then
    echo 'moving old contents of directory $CONFIG_DIR into $CONFIG/etc-backup/. Merge new and old configuration files manually if required.'
    echo 'Backup will be overriden during the next installation using this script.'
    cd $CONFIG_DIR
    [[ -d etc-backup ]] || mkdir etc-backup/
    find . -mindepth 1 -maxdepth 1 -not -name etc-backup -exec mv -f -t etc-backup/ {} \;
    cd - > /dev/null
fi

mkdir -p $CONFIG_DIR $CONFIG_DIR/secrets $BIN_DIR

cp -n  *.conf $CONFIG_DIR
cp -nr scripts/ $CONFIG_DIR
cp -n  systemd/* $SYSTEMD_DIR/

cp {backup,notify-discord} $BIN_DIR
chmod +x $BIN_DIR/{backup,notify-discord}

read -p 'repository passphrase: ' PASSPHRASE
read -p 'webhook url: ' WEBHOOK
umask 177
echo $PASSPHRASE > $CONFIG_DIR/secrets/passphrase.secret
echo $WEBHOOK > $CONFIG_DIR/secrets/webhook.secret

systemctl enable --now backup.timer

echo 'You should soon receive a confirmation message in Discord!'
$BIN_DIR/notify-discord 'meta:confirmation'

source $1
source /etc/backup/hooks/rclone.conf
echo '=> starting to clone repository'
borg with-lock $REPOSITORY rclone sync $REPOSITORY $REMOTE
echo '=> finished cloning repository'
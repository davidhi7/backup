source $1
source /etc/backup/hooks/rclone.conf
rclone sync $REPOSITORY $REMOTE
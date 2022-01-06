import sys
import os
import subprocess
import datetime
import configparser
from pathlib import Path

def load_config(filepath: Path):
    config = configparser.ConfigParser()
    config.read(filepath)
    if not config.has_section('General'):
        pass
        # TODO log
    return config

def backup(argv):
    config = load_config(Path(argv[1]))

    backup_name = datetime.datetime.now().strftime(f'%Y-%m-%dT%H:%M')
    borg_environment = {'BORG_REPO': config['General']['REPOSITORY'], 'BORG_PASSCOMMAND': 'cat ' + config['General']['PASSPHRASE_FILE']}

    if config.has_option('General', 'BACKUP_PRE_HOOK'):
        run_pre_hook(config['General']['BACKUP_PRE_HOOK'])
    
    borg_create(borg_environment, config['General']['EXCLUDE_FILE'], config['General']['SOURCE'], backup_name)
    borg_prune(borg_environment, config['Prune'])

    if config.has_option('General', 'BACKUP_HOOK'):
        run_hook(config['General']['BACKUP_HOOK'])

def run_pre_hook(command):
    # TODO impl
    pass

def run_hook(command):
    pass

def borg_create(env, borg_exclude, borg_source, backup_name):
    #cmd = ['borg', 'create', '--stats', '--exclude-from', f'"{borg_exclude}"', f'"::{backup_name}"', f'"{borg_source}"']
    cmd = f'''
    borg create --stats                 \
        --exclude-from '{borg_exclude}' \
        '::{backup_name}'               \
        '{borg_source}'   
    '''
    return exec(cmd, env)

def borg_prune(env, borg_prune_options):
    keep_daily   = borg_prune_options['KEEP_DAILY']
    keep_weekly  = borg_prune_options['KEEP_WEEKLY']
    keep_monthly = borg_prune_options['KEEP_MONTHLY']
    cmd = f'''
    borg prune --stats                      \
        --keep-daily={keep_daily}           \
        --keep-weekly={keep_weekly}         \
        --keep-monthly={keep_monthly}       \
    '''
    return exec(cmd, env)

def exec(cmd, env):
    out = subprocess.run(cmd, env=env, shell=True)
    return out.returncode 


if __name__ == '__main__':
    backup(sys.argv)

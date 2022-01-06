import sys
import os
import shutil
import subprocess
import datetime
import configparser
from pathlib import Path

def load_config(filepath: Path):
    config = configparser.ConfigParser()
    config.read(filepath)
    # do some basic validation
    if not config.has_section('General'):
        print('Configuration file is missing "General" section')
        exit(1)
    required_options = ('SOURCE', 'REPOSITORY', 'PASSPHRASE_FILE')
    for option in required_options:
        if not config.has_option('General', option):
            print('Missing required configuration file option ' + option)
            exit(1)
    return config

def backup(argv):
    if len(argv) < 2:
        print('Missing argument: backup configuration file')
        exit(1)
    config_path = Path(argv[1])
    if not config_path.is_file():
        print('Given argument doesn\'t lead to a configuration file')
        exit(1)
    config = load_config(Path(argv[1]))
    backup_name = str()
    if config.has_option('General', 'LABEL'):
        backup_name += config.get('General', 'LABEL') + '_'
    backup_name += datetime.datetime.now().strftime( f'%Y-%m-%dT%H:%M')
    print('Starting backup ' + backup_name)

    # Temporary directory to store files created for example by pre-hooks. Going to be deleted after the backup finished.
    backup_tmp_dir = Path(config['General']['SOURCE']) / f'.backup_{backup_name}'
    backup_tmp_dir.mkdir()
    
    # Environmental variables used by Borg
    borg_environment = {'BORG_REPO': config['General']['REPOSITORY'], 'BORG_PASSCOMMAND': 'cat ' + config['General']['PASSPHRASE_FILE']}

    exitcodes = dict()
    if config.has_option('General', 'BACKUP_PRE_HOOK'):
        exitcodes['prehook'] = exec(config['General']['BACKUP_PRE_HOOK'], None)
    exitcodes['create'] = borg_create(borg_environment, config['General']['EXCLUDE_FILE'], config['General']['SOURCE'], backup_name)
    exitcodes['prune']  = borg_prune(borg_environment, config['Prune'])
    if config.has_option('General', 'BACKUP_SUCCESS_HOOK') and exitcodes['create'] == 0 and exitcodes['prune'] == 0:
        exitcodes['success_hook'] = exec(config['General']['BACKUP_SUCCESS_HOOK'], None)
    if config.has_option('General', 'BACKUP_HOOK'):
        exitcodes['hook'] = exec(config['General']['BACKUP_HOOK'], None)
    shutil.rmtree(backup_tmp_dir)

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
    keep_daily   = borg_prune_options.getint('KEEP_DAILY', fallback=7)
    keep_weekly  = borg_prune_options.getint('KEEP_WEEKLY', fallback=7)
    keep_monthly = borg_prune_options.getint('KEEP_MONTHLY', fallback=12)
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

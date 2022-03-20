#!/usr/bin/env python3

import sys
import os
import shutil
import subprocess
import datetime
import argparse
import configparser
from pathlib import Path

def borg_list(config, env):
    return exec(f'borg list', borg_env)

def borg_mount(config, env, mount_point):
    if not Path(mount_point).is_dir():
        print('Mount point is not a valid directory')
        exit(1)
    return exec(f'borg mount :: {mount_point}', borg_env)

def command_create(config, borg_env):
    backup_name = str()
    if config.has_option('General', 'LABEL'):
        backup_name += config.get('General', 'LABEL') + '_'
    backup_name += datetime.datetime.now().strftime( f'%Y-%m-%dT%H:%M')
    print('=> Starting backup ' + backup_name)

    # Temporary directory to store files created for example by pre-hooks. Going to be deleted after the backup finished.
    backup_tmp_dir = Path(config['General']['SOURCE']) / f'backup_{backup_name}'
    backup_tmp_dir.mkdir(exist_ok=True)
    os.chdir(backup_tmp_dir)

    # configuration provided as environmental variables for hooks
    hook_env = config_to_env(config)

    exitcodes = dict()
    if config.has_option('General', 'BACKUP_PRE_HOOK'):
        print('=> Running prehook command')
        cmd = config['General']['BACKUP_PRE_HOOK']
        exitcodes['prehook'] = exec(config['General']['BACKUP_PRE_HOOK'], hook_env)
    print('=> Creating new archive')
    exitcodes['borg create'] = borg_create(config, backup_name, borg_env)
    print('=> Pruning repository')
    exitcodes['borg prune']  = borg_prune(config, borg_env)
    if config.has_option('General', 'BACKUP_SUCCESS_HOOK'):
        if exitcodes['borg create'] == 0 and exitcodes['borg prune'] == 0:
            print('=> Running success hook command')
            cmd = config['General']['BACKUP_SUCCESS_HOOK']
            exitcodes['success_hook'] = exec(config['General']['BACKUP_SUCCESS_HOOK'], hook_env)
        else:
            print('=> Skipping success hook, see status codes below')
    if config.has_option('General', 'BACKUP_HOOK'):
        print('=> Running hook command')
        cmd = config['General']['BACKUP_HOOK']
        exitcodes['hook'] = exec(config['General']['BACKUP_HOOK'], hook_env)

    os.chdir(backup_tmp_dir / '..')
    shutil.rmtree(backup_tmp_dir)

    print('\nFinished backup')
    print('List of exit codes:')
    print_table(exitcodes)

    if max(exitcodes.values()) >= 1:
        exit(1)
    else:
        exit(0)

def load_config(filepath: Path):
    config = configparser.ConfigParser()
    # stop converting key names to lower case, see https://stackoverflow.com/questions/19359556/configparser-reads-capital-keys-and-make-them-lower-case
    config.optionxform = str
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

def config_to_env(config):
    env = dict()
    for section in config.sections():
        for key, value in config.items(section):
            env[key] = value
    return env

def borg_create(config, backup_name, env):
    borg_source = config['General']['SOURCE']
    borg_exclude_parameter = str()
    if config.has_option('General', 'EXCLUDE_FILE'):
        borg_exclude_parameter = '--exclude-from ' + config.get('General', 'EXCLUDE_FILE')
    cmd = f'''
    borg create --stats {borg_exclude_parameter}    \
        '::{backup_name}'                           \
        '{borg_source}'   
    '''
    return exec(cmd, env)

def borg_prune(config, env):
    keep_daily   = config.getint('Prune', 'KEEP_DAILY', fallback=7)
    keep_weekly  = config.getint('Prune', 'KEEP_WEEKLY', fallback=4)
    keep_monthly = config.getint('Prune', 'KEEP_MONTHLY', fallback=12)
    cmd = f'''
    borg prune --stats                      \
        --keep-daily={keep_daily}           \
        --keep-weekly={keep_weekly}         \
        --keep-monthly={keep_monthly}       \
    '''
    return exec(cmd, env)

def exec(cmd, env):
    print(f'Executing command "{cmd}"')
    out = subprocess.run(cmd, env=env, shell=True)
    return out.returncode

def print_table(data):
    ''' Print dict of data with string keys and integer values in a fancy table '''
    longest_key = len(max(data.keys(), key=len))
    longest_val = len(str(max(data.values())))
    separator = '  |  '
    print('-' * (longest_key + longest_val + len(separator)))
    for entry in data.items():
        print(entry[0] + ((longest_key - len(entry[0])) * ' ') + separator + str(entry[1]))
    print('-' * (longest_key + longest_val + len(separator)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple borgbackup wrapper')
    parser.add_argument('command', choices=['create', 'list', 'mount'], help='Action to perform on repository')
    parser.add_argument('-c', '--config', default='/etc/backup/backup.conf', help='Path to configuration file. Default: /etc/backup/backup.conf')
    parser.add_argument('-m', '--mount-point', default='/mnt', help='Mount point used when mounting the repository. Default: /mnt')
    args = vars(parser.parse_args())

    config_path = Path(args['config'])
    if not config_path.is_file():
        print('Given argument doesn\'t specifies a valid file')
        exit(1)
    config = load_config(config_path)

    # Environmental variables used by Borg: repository and passphrase command
    borg_env = {'BORG_REPO': config['General']['REPOSITORY'], 'BORG_PASSCOMMAND': 'cat ' + config['General']['PASSPHRASE_FILE']}

    if args['command'] == 'create':
        command_create(config, borg_env)
    elif args['command'] == 'list':
        borg_list(config, borg_env)
    elif args['command'] == 'mount':
        borg_mount(config, borg_env, args['mount_point'])

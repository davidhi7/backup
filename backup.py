#!/usr/bin/env python3

import os
import sys
import shutil
import logging
import subprocess
import datetime
import argparse
import configparser
from pathlib import Path

DEBUG=bool(os.environ.get('DEBUG', False))
# file to temporarily store the log and send it in notifications
LOG_FILE='/tmp/backup.log'
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(levelname)s %(module)s: %(message)s',
    handlers=[
        logging.FileHandler(filename=LOG_FILE, mode='w'),
        logging.StreamHandler(sys.stdout)
    ])
logger = logging.getLogger(__name__)

def command_create(config, borg_env):
    backup_name = str()
    if config.has_option('General', 'LABEL'):
        backup_name += config.get('General', 'LABEL') + '_'
    backup_name += datetime.datetime.now().strftime( f'%Y-%m-%dT%H:%M')
    logger.info('=> Starting backup ' + backup_name)

    # Temporary directory to store files created for example by pre-hooks. Going to be deleted after the backup finished.
    backup_tmp_dir = Path(config['General']['SOURCE']) / f'backup_{backup_name}'
    backup_tmp_dir.mkdir(exist_ok=True)
    os.chdir(backup_tmp_dir)

    # configuration provided as environmental variables for hooks
    hook_env = config_to_env(config)

    exitcodes = dict()
    if config.has_option('General', 'BACKUP_PRE_HOOK'):
        logger.info('=> Running prehook command')
        cmd = config['General']['BACKUP_PRE_HOOK']
        exitcodes['prehook'] = exec(config['General']['BACKUP_PRE_HOOK'], hook_env)

    logger.info('=> Creating new archive')
    exitcodes['borg create'] = borg_create(config, backup_name, borg_env)
    logger.info('=> Pruning repository')
    exitcodes['borg prune']  = borg_prune(config, borg_env)

    if config.has_option('General', 'BACKUP_SUCCESS_HOOK'):
        if exitcodes['borg create'] == 0 and exitcodes['borg prune'] == 0:
            logger.info('=> Running success hook command')
            cmd = config['General']['BACKUP_SUCCESS_HOOK']
            exitcodes['success_hook'] = exec(config['General']['BACKUP_SUCCESS_HOOK'], hook_env)
        else:
            logger.warning('=> Skipping success hook due to non-zero exit code')

    if config.has_option('General', 'BACKUP_HOOK'):
        logger.info('=> Running hook command')
        cmd = config['General']['BACKUP_HOOK']
        exitcodes['hook'] = exec(config['General']['BACKUP_HOOK'], hook_env)

    os.chdir(backup_tmp_dir / '..')
    shutil.rmtree(backup_tmp_dir)

    logger.info('\nFinished backup')
    logger.info('List of exit codes:')
    logger.info(print_table(exitcodes, logger.info))

    notify = config.has_option('Notifications', 'ENABLE_NTFY') and config['Notifications'].getbool('ENABLE_NTFY')

    if max(exitcodes.values()) == 1:
        if notify:    
            send_notification(config=config, title='Warning occured', text='Warning occured during the backup. See the log for more information.', tags=['warning'])
        exit(1)
    elif max(exitcodes.values()) >= 2:
        if notify:
            send_notification(config=config, title='Error occured', text='Error occurred during backup!', tags=['rotating_light'])
        exit(2)
    else:
        exit(0)

def load_config(filepath: Path):
    config = configparser.ConfigParser()
    # stop converting key names to lower case, see https://stackoverflow.com/questions/19359556/configparser-reads-capital-keys-and-make-them-lower-case
    config.optionxform = str
    config.read(filepath)
    # do some basic validation
    if not config.has_section('General'):
        logger.critical('Configuration file is missing "General" section')
        exit(1)
    required_options = ('SOURCE', 'REPOSITORY', 'PASSPHRASE_FILE')
    for option in required_options:
        if not config.has_option('General', option):
            logger.critical('Missing required configuration file option ' + option)
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
        borg_exclude_parameter = f"--exclude-from '{config.get('General', 'EXCLUDE_FILE')}'"
    cmd = f"borg create --stats {borg_exclude_parameter} '::{backup_name}' '{borg_source}'"
    return exec(cmd, env)

def borg_prune(config, env):
    for key in ('KEEP_DAILY', 'KEEP_WEEKLY', 'KEEP_MONTHLY'):
        if key not in config['Prune']:
            logger.warning(f'prune option {key} not specified, skipping prune.')
    keep_daily   = config.getint('Prune', 'KEEP_DAILY')
    keep_weekly  = config.getint('Prune', 'KEEP_WEEKLY')
    keep_monthly = config.getint('Prune', 'KEEP_MONTHLY')
    cmd = f"borg prune --stats --keep-daily={keep_daily} --keep-weekly={keep_weekly} --keep-monthly={keep_monthly}"
    return exec(cmd, env)

def exec(cmd, env):
    cmd_fancy = ' '.join(cmd.split())
    logger.info(f'Executing command "{cmd}"')
    out = subprocess.run(cmd, env=env, shell=True)
    return out.returncode

def print_table(data, output_function):
    """Print dict of data with string keys and integer values in a fancy table to the given output function."""
    longest_key = len(max(data.keys(), key=len))
    longest_val = len(str(max(data.values())))
    separator = '  |  '
    output_function('-' * (longest_key + longest_val + len(separator)))
    for entry in data.items():
        output_function(entry[0] + ((longest_key - len(entry[0])) * ' ') + separator + str(entry[1]))
    output_function('-' * (longest_key + longest_val + len(separator)))

def send_notification(config, title, text, tags):
    """Send a notification and the log file."""
    url = '/'.join((config['Notifications'].get('NTFY_SERVER', 'https://ntfy.sh'), config['Notifications']['NTFY_TOPIC']))
    tag_str = ','.join(tags)
    exec(f'curl --upload-file "{LOG_FILE}" --Header "Filename: backup.log" "{url}"', {})
    exec(f'curl --data "{text}" --Header "Tags: {tag_str}" --Header "Title: {title}" "{url}"', {})

def excepthook(exception_type, exception_value, traceback):
    """Overwrite excepthook to send notifications when unhandled exceptions happen."""
    
    sys.__excepthook__(exception_type, exception_value, traceback)
    send_notification(config=config, title=f'Unhandled exception occurred: {exception_value}', text=traceback, tags=['rotating_light', 'rotating_light', 'rotating_light'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple borg wrapper')
    parser.add_argument('-c', '--config', default='/etc/backup/backup.conf', help='Path to configuration file. Default: /etc/backup/backup.conf')

    subparsers = parser.add_subparsers(title='command', dest='cmd', required=True)
    subparsers.add_parser(name='create', help='Run backup routine')

    exec_subparser = subparsers.add_parser(name='exec', help='Execute given command using borg-related environmental variables as defined in the configuration')
    exec_subparser.add_argument('exec', nargs=argparse.REMAINDER, help='Command to execute')
    
    args = vars(parser.parse_args())
    config_path = Path(args['config'])
    if not config_path.is_file():
        logger.critical("Given argument doesn't specifies a valid file")
        exit(1)
    config = load_config(config_path)
    sys.excepthook = excepthook

    # Environmental variables used by Borg: repository and passphrase command
    borg_env = {'BORG_REPO': config['General']['REPOSITORY'], 'BORG_PASSCOMMAND': 'cat ' + config['General']['PASSPHRASE_FILE']}

    if args['cmd'] == 'create':
        command_create(config, borg_env)
    elif args['cmd'] == 'exec':
        # nargs=argparse.REMAINDER results in a list of all remaining tokens, these need to be joined to a single string for executing
        command = ' '.join(args['exec'])
        exec(command, borg_env)

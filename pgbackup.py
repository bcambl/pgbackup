#!/usr/bin/env python
"""
A simple PostgreSQL backup rotation
-----------------------------------

A simple script to perform a full database dump using pg_dumpall.
Create a cron job for this script to run every day. Every backup will
over-write the previous months backup for the current day.

Script must be run by a user with permissions to the backup location and
ability to switch to the postgres user.
..or run as root.

Default backup file name:
/path/to/backups/pg_dumpall-<day of the month>.bz2

"""
__author__ = 'Blayne Campbell'
__date__ = '2/3/15'

from datetime import datetime
from pwd import getpwnam
import subprocess
import logging
import sys
import os

# Set location for backups:
bkp_location = '/backups/database'

bkp_user = 'postgres'
bkp_useruid = getpwnam(bkp_user).pw_uid
bkp_usergid = getpwnam(bkp_user).pw_gid
bkp_day_num = datetime.now().strftime('%d')
bkp_filename = 'pg_dumpall-%s.bz2' % bkp_day_num
bkp_command = 'su - %s -c pg_dumpall | bzip2 -vf > %s/%s' \
              % (bkp_user, bkp_location, bkp_filename)

# Ensure backup directory exists and ensure postgres has ownership
if not os.path.exists(bkp_location):
    try:
        os.makedirs(bkp_location)
        print('Created directory: %s' % bkp_location)
    except OSError as e:
        sys.exit(e)

if os.stat(bkp_location).st_uid != bkp_useruid:
    try:
        os.chown(bkp_location, bkp_useruid, bkp_usergid)
        print('Setting ownership of %s to %s' % (bkp_location, bkp_user))
    except OSError as e:
        sys.exit(e)

#  Configure Logging
FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(filename='%s/backup.log' % bkp_location,
                    level=logging.INFO)


def cleanup():
    """ Remove old backups
    """
    if os.path.isfile('%s/%s' % (bkp_location, bkp_filename)):
        try:
            os.remove('%s/%s' % (bkp_location, bkp_filename))

            logging.info('%s Removed old backup: %s/%s'
                         % (datetime.now().strftime('%Y%m%d--%H-%M-%S'),
                            bkp_location, bkp_filename))
        except OSError as e:
            sys.exit(e)


def backup():
    try:
        subprocess.check_call(bkp_command, shell=True)
        logging.info('%s Backup Created: %s/%s'
                     % (datetime.now().strftime('%Y%m%d--%H-%M-%S'),
                        bkp_location, bkp_filename))
    except subprocess.CalledProcessError:
        logging.error('Backup FAILED')
        sys.exit('Backup Failed..')


def main():
    cleanup()
    backup()

if __name__ == "__main__":
    main()

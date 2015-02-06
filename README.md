A simple PostgreSQL backup rotation
-----------------------------------

###Description
A simple script to perform a full database dump using pg_dumpall.
Create a cron job for this script to run every day. Every backup will 
over-write the previous months backup for the current day.

Script must be run by a user with permissions to the backup location and 
ability to switch to the postgres user. 
..or run as root.

Default backup file name:
/path/to/backups/pg_dumpall-<day of the month>.bz2
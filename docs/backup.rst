Backup of the LVRA data on the Oxford database
================================================

Ken has made a directory under ``/storage1/backups`` where his databases get backedup routinely. 
This is where we can regularly back up the LVRA data under the ``/storage1/backups/lasair/lvra`` 
directory. (Also backing up ``lvra_dev``). 

The database is backed up each day with a separate Year-Month-Day timestamp in the filename 
so that we don't overwrite the database during the back up. The data is important but it DOES 
exist in other places (Lasair, Rubin). 

The database contains the provenance of the LVRA, **that doesn't exist anywhere else**. If I nuke it
it's gone forever. Also it's a small (single) file so it takes no space to back up like this. 

In a cron job, doing:

.. code-block:: bash

    # Daily backup of the sqlite database in situ.
    22 10 * * * /usr/bin/cp -rp /storage1/data/lasair/lvra/db/log.db /storage1/backups/data/lasair/lvra/db/log_$(date +\%Y\%m\%d).db

    # Backup the whole directory structure somewhere else.
    10 10 * * * /usr/bin/cp -rp /storage1/data/lasair/lvra /storage1/backups/data/lasair
    30 10 * * * /usr/bin/cp -rp /storage1/data/lasair/lvra_dev /storage1/backups/data/lasair


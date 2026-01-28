Infrastructure
=================

Initiallising the directories and database
-------------------------------------------

Directories
~~~~~~~~~~~~~
On the lasair oxford servers the data are under the ``LVRA_DATA_ROOT`` directory 

There directory structure logic is as follows: TYPE > YEAR > DATE

Here the type referes to the file types:

* ``JSON``: contain the raw JSON **alert data** from Lasair LSST. 
  These are created by the ``kafka_consumer.py`` which ingests a broad Lasair filter called ``lvra_fodder``.
* ``csv``: contain the **feature csv files** created from the JSON alert data by each feature makign pipeline. 
  For example for the ``r0b`` VRA, there is a ``r0b_feature_maker.py`` script.
* ``logs``: contain log text files.
* ``db``: contain the SQLite database files. **NOTE**: this is a flat directory, no timestamped sub dirs here. 

Here is a bash script that can be run in the ``LVRA_DATA_ROOT`` of choice to create the full directory
sub-stucture. 

**STEP 1**: Save this as ``make_dirs.sh`` under the ``LVRA_DATA_ROOT`` directory.

.. code-block:: bash

    #!/usr/bin/env bash

    mkdir -p JSON
    mkdir -p csv
    mkdir -p logs
    mkdir -p db 

    years_arr=(2026 
        2027 
        2028 
        2029 
        2030 
        2031 
        2032 
        2033 
        2034 
        2035
    )
    work_dir=$(pwd)

    today=$(date +"%Y%m%d")
    today_year=$(date +"%Y")

    for dir in JSON csv logs; do
        for year in "${years_arr[@]}"; do	
            mkdir -p "$work_dir/$dir/$year"
            done
            
        mkdir -p "$work_dir/$dir/$today_year/$today"
        

    done

**STEP 2**: Run the following commands

.. code-block:: bash

    chmod u+x make_dirs.sh
    ./make_dirs.sh



SQLite database
~~~~~~~~~~~~~~~~~

Now go to the databse subdirectory. From ``LVRA_DATA_ROOT``

.. code-block:: bash

    cd db

Then copy paste this code in a new file called ``log_schema.sql``.

.. code-block:: sql

    CREATE TABLE IF NOT EXISTS feature_making (
        stem TEXT PRIMARY KEY,
        r0b INTEGER
    );

    CREATE TABLE IF NOT EXISTS annotating (
        stem TEXT PRIMARY KEY,
        r0b INTEGER
    );

    CREATE TABLE IF NOT EXISTS diaobjid_stems (
        diaObjectId INTEGER PRIMARY KEY,
        stem TEXT NOT NULL
    );


Then run:

.. code-block:: bash

    sqlite3 log.db < log_schema.sql 


.. tip::
    To ensure tables are nicely formatted when you run sqlite3 from the command line you need to 
    add a ``.sqliterc`` file in your home directory with the following content: ``.headers on`` and 
    ``.mode column`` (on two separate lines).


Logging Description
------------------------

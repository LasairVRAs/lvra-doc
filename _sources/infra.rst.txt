Infrastructure 
==================================

Architecture Overview
------------------------

Data
~~~~~~

The data are under the ``LVRA_DATA_ROOT`` directory. On the Oxford Lasair prod servers
that is ``/home/lasair/data/lvra`` (it is already defined in the ``.bashrc``). 

There directory structure logic is as follows: TYPE > YEAR > DATE

Here the type referes to the file types:

* ``JSON``: contain the raw JSON **alert data** from Lasair LSST. 
  These are created by the ``kafka_consumer.py`` which ingests a broad Lasair filter called ``lvra_fodder``.
* ``csv``: contain the **feature csv files** created from the JSON alert data by each feature makign pipeline. 
  For example for the ``r0b`` VRA, there is a ``r0b_feature_maker.py`` script.
* ``logs``: contain log text files.
* ``db``: contain the SQLite database files. **NOTE**: this is a flat directory, no timestamped sub dirs here. 


Code
~~~~~~
The code is under ``LVRA_CODE_ROOT``, it is the ``lvra`` python package. 
There are two kinds of scripts used in production: the python pipelines and their bash wrappers. 
The bash wrappers are their to set the environment so that when the code is run from cron everything 
works as expected. They also redirect the stderr to stdout and write it to an error log file so that 
cron jobs do not fail silently and we can track what is going on.

The bash scripts are under ``LVRA_CODE_ROOT/bash`` and the python scripts are under 
``LVRA_CODE_ROOT/lvra/pypeline`` (not a typo, a pun between python and pipeline. ha. ha.).


A lot of the code needs config files that are stored under ``LVRA_CODE_ROOT/data``.
Any secret information such as tokens are directly stored in environment variables on the server, 
nothing in the files. 


Useful Definitions
------------------------

* **Status Codes**: These are integers used in the database tables

+--------+---------------------------------+
| Status | Description                     |
+========+=================================+
| 0      | Initialised                     |
+--------+---------------------------------+
| 1      | Successfully Processed          |
+--------+---------------------------------+
| 21     | File Not Found (INPUT)          |
+--------+---------------------------------+
| 22     | File Not Found (OUTPUT)         |
+--------+---------------------------------+
| 23     | Not Expected Input Data Type    |
+--------+---------------------------------+
| 30     | Key Error (missing in data)     |
+--------+---------------------------------+
| 31     | Missing Columns (INPUT)         |
+--------+---------------------------------+
| 40     | Lasair Annotation Issue         |
+--------+---------------------------------+
| 41     | Failure to create Lasair client |
+--------+---------------------------------+
| 99     | Generic Error                   |
+--------+---------------------------------+

The `2X` errors refer a problem with the input or outputs such that they can't be loaded.

The `3X` errors correspond to issues with the data structure or content. So it _was_ loaded, but the contents cause problems

Code `30` likely means the files you are trying to use don't have the structure you expect. 
This is most likely due to a change in the alert or clean data format. Causes may vary:
changes in LSST data, changes in Lasair, changes in your code. 

The `4X` errors are specific to Lasair 

* **Stems**: These are the core names of our files and take the format ``YYYYMMDD_HHMMSS``.
  Each path name is constructed with the format ``TYPE/YEAR/DATE/stem.extension``.
  The stem is also used as the primary key for the status tables (see below)


Log files and SQLite database
------------------------------
Log files are written to the ``LVRA_DATA_ROOT/logs/YEAR/DAY/[logname].log`` directory.

There is also a SQLite database to keep track of the status of various processes and the 
history of the predictions of various VRAs.  It is located under ``LVRA_DATA_ROOT/db/log.db``. 

There are three kinds of tables:

* Status tables: **Used to keep a log of the status of each process in the pipeline**. The primary key is the stem and the columns are named after VRAs. Each
  cell contains a status code (see table above).

* Mapping table: primary key is the LSST ``diaObjectId`` and contains the mapping
  between the ``diaObjectId`` and the stem name. For now there is only one mapping table 
  but I make need mapping between other ids in the future... Note that here the stem
  is not technically a foreign key because I have not enforced that the stem exists in 
  the status tables. 

* Provenance table: Keeps track of the history of our model inferences/predictions, it is also where we get the scores to annotate.
  Each alert will have its own row and there may be odd cases where the same alert (`diaSourceId`) is pushed twice onto the 
  kafka stream so the table is indexed with an auto increment integer even though the diaSourceId should be unique.


Table List
~~~~~~~~~~~~~~

* ``feature_making`` [Status table]: Records which alerts files have been successfully processed.
  New columns can be added for each LVRA

+-----------------+----------+
| stem (str)      | r0b (int)|
+=================+==========+
| 20260127_105636 | 1        |
+-----------------+----------+
| 20260127_111728 | 0        |
+-----------------+----------+
| ............... | ........ |
+-----------------+----------+ 

* ``predict`` [Status table]: Records  the status of the prediction step for each feature file. 

+-----------------+----------+
| stem (str)      | r0b (int)|
+=================+==========+
| 20260127_105636 | 1        |
+-----------------+----------+
| 20260127_111728 | 0        |
+-----------------+----------+
| ............... | ........ |
+-----------------+----------+

* ``annotating`` [Status table]: Records which alerts files have been successfully annotated.
  New columns can be added for each LVRA

+-----------------+----------+
| stem (str)      | r0b (int)|
+=================+==========+
| 20260127_105636 | 0        |
+-----------------+----------+
| 20260127_111728 | 0        |
+-----------------+----------+
| ............... | ........ |
+-----------------+----------+

* ``diaobjid_stems`` : 

+--------------------+-----------------+
| diaObjectId (int)  | stem (str)      |
+====================+=================+
| 169755827469549632 | 20260128_154837 |
+--------------------+-----------------+
| 169843765851193449 | 20260128_154837 |
+--------------------+-----------------+


* ``provenance`` [provenance]: Records the mapping between LSST ``diaObjectId`` and the alert stem name.

+----+--------------------+--------------------+---------------+---------------------+------------+---------------+---------------------+
| ID | diaObjectId        | diaSourceId        | stem          | score               | model_name | model_version | timestamp           |
+====+====================+====================+===============+=====================+============+===============+=====================+
| 1  | 170019716327800983 | 170046091000545381 | 20260223_193401 | 0.963998322011434 | r0b        | a1            | 2026-02-24 05:18:57 |
+----+--------------------+--------------------+---------------+---------------------+------------+---------------+---------------------+


Log files
~~~~~~~~~~~~~~~~~

[list log fiels and explain]


Environment Variables on prod server
----------------------------------------

.. code-block:: bash

   export LASAIR_LSST_TOKEN = [see my .bashrc]
   export LVRA_TNS_API_KEY = [see my .bashrc]

    # Changing the name of this env variable breaks Lasair VRA
    export LASAIR_LSST_DEV_TOKEN=[see my .bashrc]
    export LASAIR_LSST_TOKEN=[see my .bashrc]
    export LVRA_DATA_ROOT="/home/lasair/data/lvra/"
    export LVRA_DATA_ROOT_DEV="/home/lasair/data/lvra_dev/"
    export LVRA_CODE_ROOT="/home/lasair/code/lvra/"
    # Add to my python path
    export PYTHONPATH=$PYTHONPATH:/home/lasair/code/lvra/
    export LVRA_TNS_API_KEY=[see my .bashrc]
    # add some useful aliases
    alias cdlvradat='cd $LVRA_DATA_ROOT'
    alias cdlvra='cd /home/lasair/code/lvra'
    alias tnsreport='/home/lasair/code/tns/tns_report.py'


Infra Set-up Instructions
-------------------------------

Directories
~~~~~~~~~~~~~~

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

    CREATE TABLE feature_making (
        stem TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL DEFAULT current_timestamp,
        r0b INTEGER
    );
    CREATE TABLE annotating (
        stem TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL DEFAULT current_timestamp,
        r0b INTEGER
    );
    CREATE TABLE diaobjid_stems (
        diaObjectId INTEGER PRIMARY KEY,
        stem TEXT NOT NULL,
        timestamp TEXT NOT NULL DEFAULT current_timestamp
    );
    CREATE TABLE provenance (
        ID INTEGER PRIMARY KEY, 
        diaObjectId INTEGER,
        diaSourceId INTEGER, 
        stem TEXT,
        score REAL,
        model_name TEXT,
        model_version TEXT,
        timestamp TEXT NOT NULL DEFAULT current_timestamp
    );
    CREATE TABLE threshold_flags_provenance(
        ID INTEGER PRIMARY KEY,
        diaObjectId INTEGER,
        diaSourceId INTEGER,
        stem TEXT,
        n_gt22 INTEGER,
        n_gt21 INTEGER,
        n_gt20 INTEGER,
        n_gt19 INTEGER,
        n_gt18 INTEGER,
        brighter22 INTEGER,
        brighter21 INTEGER,
        brighter20 INTEGER,
        brighter19 INTEGER,
        brighter18 INTEGER,
        first22 INTEGER,
        first21 INTEGER,
        first20 INTEGER,
        first19 INTEGER,
        first18 INTEGER,
        timestamp TEXT NOT NULL DEFAULT current_timestamp
    );
    CREATE TABLE predict (
        stem TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL DEFAULT current_timestamp,
        r0b INTEGER
    );



Then run:

.. code-block:: bash

    sqlite3 log.db < log_schema.sql 


.. tip::
    To ensure tables are nicely formatted when you run sqlite3 from the command line you need to 
    add a ``.sqliterc`` file in your home directory with the following content: ``.headers on`` and 
    ``.mode column`` (on two separate lines).


Local dev env
----------------

I have not set up a docker (and will not for now) but I have local directories that mimick what is on remote. 

Most importantly I have environments that need to be the same. 

conda
~~~~~~~~~~~~~~~~~

For the python environment I exported a `yaml` file of the remote conda environement:

.. code-block:: bash

    conda env export --no-builds > lvra_env.yml

Then I copied it in my local package:

.. code-block:: bash

   scp lasair@oxdb1:code/lvra_env.yml ./software/lvra 

Then I created the environment with:

.. code-block:: bash

    conda env create -f software/lvra/lvra_env.yml  -n lvra




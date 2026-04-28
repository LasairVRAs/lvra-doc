Dev environement
=============================

Making a fresh dirctory 
------------------------

**Remote Oxford Server**: Made new directory under ``./data/lvra_dev`` (actually a symlink placed in storage). 
Made a file to create the directory structure and the database tables. It is different from the 
local testing file because I'm not recreating the full LasairOxford severver directory base 
``code`` and ``data`` or copying the bash scripts under that code base. It already exists here as is.

.. code-block:: bash

    #!/usr/bin/env bash

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

    today=$(date +"%Y%m%d")
    today_year=$(date +"%Y")

    #mkdir -p "test_$today"

    #cd "test_$today"

    #mkdir -p data/lvra
    #mkdir -p code

    cd $LVRA_DATA_ROOT_DEV

    work_dir=$(pwd)

    mkdir -p JSON
    mkdir -p csv
    mkdir -p logs
    mkdir -p db


    for dir in JSON csv logs; do
        for year in "${years_arr[@]}"; do
            mkdir -p "$work_dir/$dir/$year"
            done

        mkdir mkdir -p "$work_dir/$dir/$today_year/$today"


    done

    cd "$work_dir/db"

    cat > log_schema.sql <<'SQL'
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
    SQL

    sqlite3 log.db < log_schema.sql


Check-list 
-------------

1. Comment out the cron job
2. Make fresh dev branch from ``main``
3. Change ``public_settings.yml`` to point to the lasair dev server 
4. Change ``r0b_config.yml`` so topic out points to dev annotator (and ammend any other relevant settings)
5. MAKE SURE YOUR ``lasair83_lvra_feed_full`` is the same as the one on prod so we are ingesting same alerts in same format
6. Do what you need to do
7. **CHECKOUT MAIN AND TURN OUT THE CRON JOB AGAIN**
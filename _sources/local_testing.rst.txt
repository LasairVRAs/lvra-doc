Testing Procedure
=============================

Making a fresh dirctory 
------------------------

**Remote Oxford Server**: Made new directory under `./data/lvra_dev` (actually a symlink placed in storage). 


**My Local Machine**: Made the file ``make_local_test_env.sh`` in ``ox_lvra`` so I don't touch the ``data`` and ``code`` directories that 
I know are working like on the server.

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

    mkdir -p "test_$today"

    cd "test_$today"

    mkdir -p data/lvra
    mkdir -p code 

    cd data/lvra

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

    ## DATA 
    TEST_JSON_NAME=/home/stevance/oxlvra_dev/data/lvra/JSON/2026/20260202/20260202_102448.json
    JSON_LAST_DIR_AND_NAME=${TEST_JSON_NAME: -34}

    # Putting some data in the JSON directory
    mkdir -p "$work_dir/JSON/${JSON_LAST_DIR_AND_NAME:: 14}"
    cp -p $TEST_JSON_NAME $work_dir/JSON/$JSON_LAST_DIR_AND_NAME

    ## CODE
    cd "/home/stevance/oxlvra_dev/test_$today"
    cd code
    mkdir -p lvra/bash
    cd lvra/bash
    cp -p /home/stevance/oxlvra_dev/code/lvra/bash/r0b_feature_maker.sh .
    cp -p /home/stevance/oxlvra_dev/code/lvra/bash/r0b_predict.sh .
    cp -p /home/stevance/oxlvra_dev/code/lvra/bash/r0b_annotator.sh .



Add data to sqlite database
------------------------------

This would have been done by the kafka consumer but we're not runnign it here so we have to simulate
those entries

.. code-block:: sql

    insert into feature_making (stem, r0b) values ('20260202_102448', 0) on conflict (stem) do update set r0b=excluded.r0b;
    insert into annotating (stem, r0b) values ('20260202_102448', 0) on conflict (stem) do update set r0b=excluded.r0b;


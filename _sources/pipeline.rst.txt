Pipeline Overview
==========================

This page provides an overview of the LVRA production pipeline (**does not include training procedure**) that is currently on the Oxford Lasair server. 


Quick Summary of the workflow
--------------------------------

1. **Kafka consumer**: listens to the Kafka stream from Lasair, saves the alerts to a **JSON file** and initialises rows in relevant tables in the database.
2. **Feature making**: turns raw alerts in JSON files into features in a **csv file**; updates the status of the feature_making status table in the database.
3. **Predict**: runs the inference step, puts the scores in the "provenance" table in the database which keeps track of the history of our scores; updates the predict status table.
4. **Annotator**: reports the scores (and any other quantities we chose) to Lasair via the annotator functionality of the lasair client code. 

These steps are run by python scripts that are wrapped in their own bash wrapper which sets the environment and does some bookkeeping like creating log files that don't exist. 
The pipeline is run every 5 minutes from a cron job which triggers an orchastrator file called ``bigbashboy.sh``.

**Now here are the details...**


Step 1: Kafka
-------------------------------


The first step is to consume our kafka queue from Lasair. 
In production the filter we listen to is **lvra-fodder**.
It is a private filter so only me (Heloise) has access to it to modify or view the query, so I have put the SQL query for this filter in an appendix
at the bottom of this page. 


The kafka_consumer.py script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Inputs:
    - ``public_settings.yaml``: contains the kafka server, group ID, topic name, base directory for outputs (data, logs, lockfiles)
    - The kafka stream from our filter, which we connect to using the settings from the YAML file.
* Outputs:
    - **One JSON file containing all alerts consumed in this run of the script**. The JSON file is created with format ``[stem].json`` (**see definition of stem below**). For exact directory structure see the "Infrastrucutre" page of the manual. 
    - A new row in the tables ``feature_making``, ``predict`` and ``annotating`` in the SQLite database. These tables are **essentially logs of the status of each process**, 
      they show a **status code** (an integer, see table in Infrastrucutre for details) for **each stem** and each LVRA (currently there is only one: r0b).
    - Exit code (0 if successful, otherwise the status code returned by whatever error occured)

.. admonition:: Status code initialised to 0 by the kafka consumer 

    When the kafka consumer runs it sets the **status of each process to 0**, meaning we expect the processes (making the features, the predictions, sending annotations)
    to be run very soon for the alerts of the given stem. The status will be changed in subsequent steps depending on success or failure. 

The JSON files are created atomically, meaning that the data is written to a temp file whilst the alerts are being consumed. This way if the process fails in the middle 
of this process we do not have a JSON file with corrupted data entering the rest of the pipeline. 
**Only once the writting is complete and the file renamed** do we initialise the rows to the status tables 
in the database. 


What is a stem?
~~~~~~~~~~~~~~~~~~~~~~~~~

A word of jargon that will come up over and over again is **"stem"**, which is the name of the JSON and CSV files created as the pipeline runs. 
The stem is constructed as ``YYYYMMDD_HHMMSS`` (UTC) and **is the same for the JSON and CSV files that are realted** to each other, so that they are easy to associate. 


The pipeline is triggered by a cron job every 5 minutes, and for each run there is a unique stem. Each file contains data for many alerts, all processed in the same run, 
and they can be identified (files and database) by that stem.

.. tip:: 

    **The main take away is that the path name of the data files are constructed with the format ``TYPE/YEAR/DATE/stem.extension``.**
    This allows the pipeline the dynamically construct the paths of files based on the stem recorded in the database. 
    The naming convention is therefore critical to the functioning of the pipeline - **DO NOT RENAME FILES UNLESS YOU KNOW WHAT YOU ARE DOING**.


* **Stems**: These are the core names of our files and take the format ``YYYYMMDD_HHMMSS``.
  
  The stem is also used as the primary key for the status tables (see below)


Exit code Vs Status code: is 0 good or bad then?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You may have noticed above that I use 0 as a status code in the status tables to show that a process is waiting to be run, but I also use it as an one of the exit code for the pythons scripts.

Generally speaking the exit codes of the files are *mostly* the same as the status codes (see Infrastructure page for a table summarising the status codes), 
**except** for the success case. For the *status codes* 0 is used as an initialisation status code and 1 is a success (1 == good is very "python").
However when dealing with **exit codes, they end up as outputs in my bash wrapper scripts. In bash 0 == success, anything else is a failure of some kind.**

So the python scripts do perform some gymnastics to turn the status codes into exit codes that makes sense when the python is executed as part of a larger pipeline in a bash 
orchestrator script.


Step 2: Feature making
------------------------

The ``r0b_feature_maker.py`` script transforms the raw alerts (JSON files) into features (csv files) that can be used to do inference (predictions). 

* Inputs:
    - ``public_settings.yaml`` because it contains the base directory
    - The JSON file created by the kafka consumer. To know which JSON files to process it reads the ``feature_making`` table and selects the stems for all rows where the status flag is not 1 or -1 (success or partial success). 
* Outputs:
    - A csv file with name ``[stem].csv`` 
    - Updates the ``feature_making`` table in the database with a status flag (see table in the "Infrastructure" page of the manual for the error codes). 
    - Updates other relevant tables, such as the ``threshold_flags_provenance`` table in the case of r0b. 
    - Exit code (0 if successful, otherwise the status code returned by whatever error occured)

The creation of the feature dataframes which are then written out to csv is not entierly trivial. 
Indeed the kafka stream from lasair contains some Lasair features that are indexed on the ``diaObjectId`` and the full Rubin packet that is indexed on the ``diaSourceId``.
Exactly how and which features are created will be dependent on the specific LVRA; consult the relevant pages to get these details. 


Step 3: Predict
------------------------

The inference step is done by the ``r0b_predict.py`` script.

* Inputs:
    - ``public_settings.yaml`` because it contains the base directory
    - ``r0b_config.yaml``: Contains the path to the ``.joblib`` file, the model name and the model version (and other settings only relevant for the next step)
    - The csv files containing the features. To know which csv files still need to be processed the ``predict`` table is consulted to find the stems with status not 1 or -1.
* Outputs:
    - Adds a row to the ``provenance`` table for each alert in the csv file. 
    - Updates the ``predict`` table in the database with a status flag (see table in the "Infrastructure" page of the manual for the error codes).
    -  Exit code (0 if successful, otherwise the status code returned by whatever error occured)


Why a provenance table?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The provenance table in the database records the score given to **each alert**. In Lasair the annotations are indexed by ``diaObjectId``, that is the astrophysical event, not the lightcurve
data point. This means that when a new lightcurve point arrives in the alerts, the pipeline makes a new prediction and the new annotation in Lasair **overwrites** the previous one.

Lasair therefore provides no history on the scores. This is a problem for testing and validation, but also because we may want to use the score history to make decisions in the future, 
or add them to the additional data that we can report in the annotation through the ``class_dict`` (a free from dictionary) field. 


Step 4: Annotator
------------------------

Finally we can report the scores and other quantities to Lasair via annotations. This is done by the ``r0b_annotator.py`` script.

* Inputs:
    - ``public_settings.yaml`` because it contains the base directory
    - ``r0b_config.yaml``: Contains the model name, model version, the topic of the annotator, the explanation and URL settings we'll pass on to the lasair annotator. 
    - The ``annotatin`` table which tells us which stems have already had their alerts annotated. 
    - The ``provenance`` table which contains the scores for each alert (and a stem column so we only grab the relevant alerts).
* Outputs:
    - Sends alerts to the Lasair annotator. 
    - Updates the ``annotating`` table in the database with a status flag (see table in the "Infrastructure" page of the manual for the error codes).
    - Exit code (0 if successful, otherwise the status code returned by whatever error occured)


.. tip::
    The annotator can take the Lasair token as a command line argument. This is useful if you want to test pushing annotations to the dev lasair server. 
    The bash wrapper sets the environment variable ``LASAIR_TOKEN`` (which is called in the python script) to the argument pass on the CL. 
    Otherwise it looks for the ``LASAIR_LSST_TOKEN`` environment variable, which is the token for the production server. 


``bigbashboy.sh`` - the orchestrator script
---------------------------------------------

Although each python script already has a bash wrapper to set the environment, the pipeline needs to be called in a crontab. 
The problem is that **each process needs to finish before the next on is called** (ideally), also I have issues with the logs not going where
I wanted them to go... Anyways, the ``bigbashboy.sh`` script calls each step and does a whole lot of **bookkeeping**.
It checks that each file exists, **creates lock files** so that we don't have multiple instances of a feature making process happening and files being over written.
(it can happen if you run a bash script whilst a cron job has triggered).

It also creates a high level log file so you can check the pipeline is running without having to open each individual log.


Appendices
--------------

A: SQL for the filter
~~~~~~~~~~~~~~~~~~~~~~

When I do "Show Filter" in Lasair, this is what I see. If you want to recreate the filter, copy past the columns into the SELECT box of the filter making page, 
then copy paste the WHERE conditions into the WHERE box. The table names are automatically populated. I also ask for the full stream as the 
pypeline expects the full Rubin packet for each alert. 

.. code-block:: sql

    SELECT COLUMNS:
    objects.diaObjectId,
    objects.lastDiaSourceMjdTai,
    objects.latestR,
    objects.nDiaSources,
    objects.ebv,
    objects.ra,
    objects.decl,
    objects.tns_name,
    objects.absMag,
    objects.absMagMJD,
    objects.firstDiaSourceMjdTai,
    sherlock_classifications.separationArcsec,
    sherlock_classifications.direct_distance,
    sherlock_classifications.distance,
    sherlock_classifications.z,
    sherlock_classifications.photoZ,
    sherlock_classifications.photoZErr,
    sherlock_classifications.physical_separation_kpc,
    sherlock_classifications.classification as sherlock_classifications,
    objects_ext.nDiaSources,
    objects_ext.raErr,
    objects_ext.decErr,
    objects_ext.ra_dec_Cov
    FROM:
    sherlock_classifications,objects_ext,objects
    WHERE:
    objects.nDiaSources >= 2
    AND sherlock_classifications.classification in ('ORPHAN', 'SN','NT', 'UNCLEAR')
    AND objects.latestR > 0.5
    ORDER BY objects.lastDiaSourceMjdTai DESC

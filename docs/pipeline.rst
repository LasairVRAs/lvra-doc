Pipeline Overview
==========================

This page provides an overview of the LVRA production pipeline (**does not include training procedure**) that is currently on the Oxford Lasair server. 

What is a stem?
------------------

A word of jargon that will come up over and over again is **"stem"**, which is the name of the JSON and CSV files created as the pipeline runs. 
The stem is constructed as ``YYYYMMDD_HHMMSS`` (UTC) and is the same for the JSON and CSV files that are realted to each other, so that they are easy to associate. 

The pipeline is triggered by a cron job every 5 minutes, and for each run there is a unique stem. Each file contains data for many alerts, all processed in the same run, 
and they can be identified (files and database) by that stem. 


Step 1: kafka
---------------

The first step is to consume our kafka queue from Lasair. In the production server the filter we listen to is ``lvra-fodder`` (topic name: ``lasair_18lvra-fodder``).
The SQL query for this filter can be found at the bottom of this page. 

The ``kafka_consumer.py`` script:

* Inputs:
    - ``public_settings.yaml``: contains the kafka server, group ID, topic name, base directory for outputs (data, logs, lockfiles)
    - Lasair Kafka stream, which the stream connects to using the settings from the YAML file.
* Outputs:
    - **One JSON file containing all alerts in this batch**. The JSON file is created with format ``[stem].json``. For exact directory structure see the "Infrastrucutre" page of the manual. 
    - A new row in the tables ``feature_making``, ``predict`` and ``annotating`` in the SQLite database, with the stem and a status flag of 0 for each LVRA column (currently there is only one LVRA: r0b). 
    - Exit code (0 if successful, otherwise the status code returned by whatever error occured)

The JSON files are created atomically, meaning that during the kafka consumption process the data is written to a temp file. This way if the process fails in the middle  
we do not have a JSON file with corrupted data entering the rest of the pipeline. Only once the writting is complete is the file renamed and the rows added to the status tables 
in the database. 


The python script ``kafka_consumer.py`` is paired with a bash script called ``kafka.sh`` which sets the environment and the python path, checks whether the log file exists 
(and creates one is necessary), then runs the python script. It is the ``kafka.sh`` script that is called in the ``bigbashboy.sh`` script (see below) that is run by the cron job.


Exit code Vs Status code: is 0 good or bad then?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The exit codes of the files are _mostly_ the same as the status codes (see Infrastructure page), **except** for the success case. 0 is used as an initialisation status code and 1 is a success. 
(1 == good is very "pyhton"), however when dealing with **exit codes, these end up as outputs in my bash wrapper scripts. In bash 0 = success, anything else is a failure of some kind.**
So the python scripts do perform some gymnastics to turn the status codes into exit codes that makes sense when the python is executed as part of a larger pipeline in a bash 
orchestrator script.


Step 2: Feature making
------------------------

The ``r0b_feature_maker.py`` script transforms the raw alerts into features that can be used to do inference (predictions). 

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

The python script ``r0b_feature_maker.py`` is paired with a bash script called ``r0b_feature_maker.sh`` which sets the environment and the python path, checks whether the log file exists 
(and creates one is necessary), then runs the python script. It is the ``r0b_feature_maker.sh`` script that is called in the ``bigbashboy.sh`` script (see below) that is run by the cron job.


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


The python script ``r0b_predict.py`` is paired with a bash script called ``r0b_predict.sh`` which sets the environment and the python path, checks whether the log file exists 
(and creates one is necessary), then runs the python script. It is the ``r0b_predict.sh`` script that is called in the ``bigbashboy.sh`` script (see below) that is run by the cron job.


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

The python script ``r0b_annotator.py`` is paired with a bash script called ``r0b_annotator.sh`` which sets the environment and the python path, checks whether the log file exists 
(and creates one is necessary), then runs the python script. It is the ``r0b_annotator.sh`` script that is called in the ``bigbashboy.sh`` script (see below) that is run by the cron job.


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

SQL for the filter
~~~~~~~~~~~~~~~~~~~~~

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

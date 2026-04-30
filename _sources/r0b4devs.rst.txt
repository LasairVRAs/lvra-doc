LVRA:r0b 
========================

*Note that this documentation is mostly aimed at developers that will have to maintain or further develop the code base*


Feature making logic 
-------------------------------

The code invovled in making the features for r0b is split between the main ``pypeline/r0b_feature_maker.py`` module, and the ``utils/features.py`` utility module. 
``pypeline/r0b_feature_maker.py`` contains **operational logic and some feature engineering/cleaning**: 
* [Operational]: loading settings, connecting to the databse, querying the database to know which files (stems) have yet to be processed, logging, etc. 
* [Feature engineering/cleaning]: calculating new quantities (delta MJD between first detection and current observation), dropping unwanted columns  


The ``misc/features.py`` does all the dirty work of **data cleaning/formating** as well as doing **feature engineering on the full lightcurve of each alert**. 


To help visualise the journey of the data, I present below the tables of data at different stages of the feature making process, 
refering to them by the **variable name used in the code**. This page is mostly a helper for developers learning the code base, 
so they can visualise what the pandas dataframes look like at each stage. 


The data from the JSON file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As mentioned in the Pipeline Overview, the data we get from the kafka stream has a partially nested structure. 
There are a number of features we get directly from our Lasair filter (see query in Appendix A of the Pipeline Overview), such as the ``diaObjectId``, ``latestR``, ``ebv``, etc...
There is also a field called ``alerts`` which contains the *full alert packet from Rubin** (except image cut-outs). 

If you are not familiar with the structure of these data I recommend checking my `Lasair Kafka tutorial notebook <https://github.com/LasairVRAs/lasair_user_tutorials/blob/main/KAFKA_Listen_to_Alerts.ipynb>`__ 
(Section 6: Full Packet Data).

In the utility function ``lvra.utils.features.json2cleandf()``, the ``json_df`` variable contains the FULL JSON file loaded into a dataframe, 
and it looks something like this [NOTE - **you can scroll sideways**]:

.. list-table::
   :header-rows: 1

   * - 
     - diaObjectId
     - lastDiaSourceMjdTai
     - latestR
     - nDiaSources
     - ebv
     - ra
     - decl
     - tns_name
     - absMag
     - absMagMJD
     - firstDiaSourceMjdTai
     - separationArcsec
     - direct_distance
     - distance
     - z
     - photoZ
     - photoZErr
     - physical_separation_kpc
     - sherlock_classifications
     - raErr
     - decErr
     - ra_dec_Cov
     - UTC
     - alerts
   * - 0
     - 169760231711572988
     - 61029.4
     - 0.838478
     - 2
     - 0.103305
     - 223.024
     - -41.4592
     - nan
     - nan
     - nan
     - 61029.3
     - nan
     - nan
     - nan
     - nan
     - nan
     - nan
     - nan
     - ORPHAN
     - 2.14003e-06
     - 2.82303e-06
     - 4.63027e-13
     - 2026-02-04 11:51:46
     - NaN
   * - 1
     - 169355603258900842
     - 61069.1
     - 0.996714
     - 33
     - 0.00812477
     - 9.22276
     - -45.5966
     - nan
     - nan
     - nan
     - 60937.3
     - nan
     - nan
     - nan
     - nan
     - nan
     - nan
     - nan
     - ORPHAN
     - 1.37756e-05
     - 2.42808e-05
     - -8.48339e-11
     - 2026-02-04 11:53:03
     - {'diaObject': {'diaObjectId': 1697602317115729...


Here I've given two examples of alerts, one where the ``alerts`` field (Rubin alert packet) is empty, one where it is populated with a nested dictionary (you can't see the whole thing
it's massive). 

**The alert packets should not be missing, but it has happened in the past** during comissioning, so the code is built to be robust to this 
and allow the processing to continue and just ignore this specific event (a.k.a ``diaObject``), logging the ``diaObjectId`` with missing packets in the logs. 


The Lasair filter features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We can easily recover the columns that we selected in our Lasair filter query by saveing all the columns except the last ones to a dataframe
 ``filterOutput_df = json_df.iloc[:,:-1]``, which we will later join with the other features from the lightcurve. 

 I am not providing a table because it is the same as above, save for the last column being dropped. 


The features associated with the latest lightcurve point
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To access all of the lightcurve features provided by Rubin (e.g. SNR, psf fitting related fields, etc... )
we need to access the nested dictionaries in the ``alerts`` columns, specifically the ``diaSourcesList`` table which contains 
the packet data for lightcurve points. 

The first kind of feature we want to recover, is all of the data about the **most recent source**. 
Below I show a *truncated* example of the dataframe containing the lightcurve features. 
If you want to see the full list of columns, go to the Rubin schema explorer; here is `a link to the diaSource table schema <https://sdm-schemas.lsst.io/apdb.html#DiaSource>`_ 
In the ``json2cleandf()`` function, the dataframe with this format is called ``latestSourceIds_df`` because it is constructed such that each row
gives use the values for the last lightcurve point (``diaSourceId``) for a given astrophysical event (``diaObjectId``). 

.. list-table::
   :header-rows: 1

   * - 
     - diaSourceId
     - visit
     - detector
     - diaObjectId
     - ssObjectId
     - parentDiaSourceId
     - midpointMjdTai
     - ra
     - raErr
     - decErr
     - ra_dec_Cov
     - x
     - xErr
     - y
     - yErr
     - centroid_flag
     - apFlux
     - apFluxErr
     - apFlux_flag
     - apFlux_flag_apertureTruncated
     - isNegative
     - snr
     - psfFlux
     - psfFluxErr
     - ...
     - decl

   * - 0
     - 169562325818802242
     - 2025110400302
     - 183
     - 169562325818802242
     - nan
     - 0
     - 60984.2
     - 10.1346
     - 3.25122e-05
     - 3.94188e-05
     - -6.12409e-10
     - 2451.23
     - 0.917773
     - 2333.35
     - 0.539348
     - False
     - 1246.3
     - 1128.77
     - False
     - False
     - False
     - 6.38317
     - 3336.28
     - 526.842
     - ...
     - -42.4024

   * - 1
     - 169584317122478660
     - 2025110900310
     - 178
     - 169562325818802242
     - nan
     - 0
     - 60989.2
     - 10.1347
     - 1.41809e-05
     - 1.91613e-05
     - -3.45086e-13
     - 3742.17
     - 0.345846
     - 2336.37
     - 0.345686
     - False
     - 2743.54
     - 485.996
     - False
     - False
     - False
     - 10.5507
     - 2424.67
     - 228.346
     - ...
     - -42.4024




.. admonition:: Note on dataframe concatenation 

    In the code ``latestSourceIds_df``  is constructed by concatenating a list of single-row dataframes created in a loop and stored in a list 
    (``latestSourceId_dfList``) before final concatenation. This is because concatenating increasingly large dataframes in a loop is 
    computationally inefficient and the loops gets increasingly slow (or at least it's been my experience, maybe by the time you read this
    they'll have fixed it). AFAIK it is because the concatenation operation makes a copy of the dataframe, so if you are dealing 
    with an increasingly large table to copying gets more and more expensive. 

    By contrast python list elements just "point" (there's no actual pointers in python) to where that element is stored in memory. 
    Adding to that list is super cheap. Then the final concatenation is just one operation after completion of the for-loop. 




The features associated with the lightcurve history
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Although the current version of r0b only uses the Lasair filter columns and the lightcurve features associated with the latest point to calculate a score, 
the annotator is build to provide additional flags and information that is not otherwise available in the Lasair filters. 

Namely:

- **n_gtXX** (e.g. n_gt22): The number of lightcurve points with magnitude BIRGHTER than 22nd, 21st, 20th, 19th or 18th magnitude. 
- **brighterXX** (e.g. brighter22): A boolean flag indicating whether there is at least one point brighter than 22nd, 21st, 20th, 19th or 18th magnitude.
- **firstXX** (e.g. first22): A boolean flag indicating whether this is the first time the transient has crossed a given magnitude threshold_flags_provenance

.. important::

    Note that the "brighter22" (or other threshold) flag tells you if an object has EVER been brighter than that threshold. It may be fainter now. 
    The reason is that in your filter you can easily check with the flux for a current alert is brighter than a chosen threshold but you **do not**
    have an easy way to set a condition on the lightcurve history. You would have to download the lightcurve data through your kafka stream 
    and process the data. *Since I'm processing all that data anyway, I might as well provide that information as part of the annotator*. 


These are constructed by the utility function ``utils.features.flux_threshold_features()`` which is called *within* ``utils.features.json2cleandf()`` where 
these flags are joined to the final clean dataframe along ``filterOutput_df`` and ``latestSourceIds_df``.

The clean data frame that comes out of the ``json2cleandf()`` function looks something like this. Note I have truncated it, showing 
that the leftmost columns come from the ``latestSourceIds_df`` dataframe, the middle columns come from the ``filterOutput_df`` dataframe, 
and the rightmost columns are the flags associated with the lightcurve history.

.. list-table::
   :header-rows: 1

   * - 
     - diaSourceId
     - visit
     - detector
     - ssObjectId
     - ...
     - diaObjectId
     - lastDiaSourceMjdTai
     - latestR
     - nDiaSources
     - ebv
     - ...
     - is_above_20 		
     - first_time_20
     - N_above_20
     - ...

   * - 0
     - 169562325818802242
     - 2025110400302
     - 183
     - nan
     - ...
     - 169562325818802242
     - 2025110400302
     - 183
     - 169562325818802242
     - nan
     - ...
     - True		
     - True
     - 1
     - ...




Delta MJD feature and dropped columns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before creating the csv that will be used to calculated the r0b score, we also calculate the delta MJD ``['deltaDiaSourceMjdTai']``, and 
then we drop the following columns: 

.. code-block:: python 

    COLUMNS_TO_REMOVE = ['visit', 
                     'tns_name',
                     'ssObjectId',
                     'parentDiaSourceId',
                     'midpointMjdTai',
                     'timeProcessedMjdTai',
                     'timeWithdrawnMjdTai',
                     'firstDiaSourceMjdTai',
                     'ra_sourceId',
                     'raErr_sourceId',
                     'decErr_sourceId',
                     'ra_dec_Cov_sourceId',
                     'UTC',
                    ]
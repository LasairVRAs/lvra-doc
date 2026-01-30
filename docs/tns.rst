TNS Reporting
===========================

The Lasari Virtual Research Assistants can report to TNS using the Lasair (group) LVRA (bot). 
It has a specific API key that is stored in my envrionment variables and I need to add 
to my TNS report:

``tns_marker{"tns_id":197854,"type": "bot", "name":"LVRA"}``

Setting up TNS reporting of LSST alerts through the TNS API
-------------------------------------------------------------------
There is a `TNS manual from January 2025 <https://www.wis-tns.org/sites/default/files/api/tns2_manuals/TNS2.0_bulk_reports_manual.pdf>`_.
The schema is basically on page 7 to 9 (for reporting). 

Here is an example of the data we send in the packet to TNS for an ATLAS report. 

.. caution::
    I have marked the mandatory fields with a ``*`` below but they need removing for the actual JSON. Same for the comments as JSON is data only. 


**Mandatory fields**
~~~~~~~~~~~~~~~~~~~~~

* ``[ra][value]``
* ``[dec][value]``
* ``reporting_group_id``
* ``data_source_groupid``
* ``at_type``
* ``[non_detection][archiveid]`` 
* ``[photometry]``: ``obsdate``, ``flux``, ``flux_unitid``, ``filterid``, ``instrumentid``

**Important codes to know for LSST**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* ``instrumentid``: 287
* ``reporting_group_id``: 111
* ``filterid``: 
    * u: 160
    * g: 161
    * r: 162
    * i: 163
    * z: 164
    * y: 165
* ``flux_unitid``: 34 (nJy)
* ``data_source_groupid``: 165 (rubin)

.. warning::
    Not sure if the ``data_source_groupid`` is right. I've put down the one for Rubin on TNS owned by Eric Bellm.


``at_type``
~~~~~~~~~~~~~~~~~~~~~~~~~

+------+-------------------------------+
| Code | Description                   |
+======+===============================+
| 0    | Other - Undefined             |
+------+-------------------------------+
| 1    | PSN - Possible SN             |
+------+-------------------------------+
| 2    | PNV - Possible Nova           |
+------+-------------------------------+
| 3    | AGN - Known AGN               |
+------+-------------------------------+
| 4    | NUC - Possibly nuclear        |
+------+-------------------------------+
| 5    | FRB - Fast Radio Burst event  |
+------+-------------------------------+


``archiveid``
~~~~~~~~~~~~~~~~~~~~~~~~~

+------+-------------------------------+
| Code | Description                   |
+======+===============================+
| 0    | Other - Undefined             |
+------+-------------------------------+
| 1    | SDSS                          |
+------+-------------------------------+
| 2    | DSS                           |
+------+-------------------------------+


Other Notes
~~~~~~~~~~~~~~~~~~~~~
* The JSON report schema can be explored on the `sandbox <https://sandbox.wis-tns.org/api/get/values>`_ 
* ``internal_ids``: can have up to five subfields. For LSST should contain the ``diaObjectId``, the ``diaSourceId`` of trigger. **_anything else?_**
* ``internal_name`: LSST ``diaObjectId``
* ``filter_value`` and ``instrument_value``: Find the ones I need for LSST. 
* ``[non_detection][archiveid]``: in Pstarrs ken uses archive_id = 2 (we think is SDSS);  could be 0 if no specific catalogue. This is relevant for LSSST
    because if we find and report the transient on the first alert there will be no forced phot. Even if we ware on the second go around,
    forced phot may not be enough to determine with confidence the last non-detection. So we may just use the place-holder. 
* 




.. code-block:: json

    {
        "at_report": {
            "0": {
                "at_type": "1",
                "dec": {
                    "value": "-33.250264" 
                }, 
                "discovery_data_source_id": "18", 
                "discovery_datetime": "2026-01-11.22008", 
                "internal_ids": {
                    "internal_name": "ATLAS26afg", 
                    "internal_objid": "1003019830331501200"
                }, 
                "internal_name": "ATLAS26afg", 
                "non_detection": {
                    "exptime": "30.0", 
                    "filter_value": "71", 
                    "flux_units": "1", 
                    "instrument_value": "256", 
                    "limiting_flux": "19.17", 
                    "obsdate": "2026-01-10.08145", 
                    "observer": "Robot"
                }, 
                "photometry": {
                    "photometry_group": {
                        "0": {
                            "comments": "", 
                            "exptime": "30.0", 
                            "filter_value": "72", 
                            "flux": "18.257", 
                            "flux_error": "0.139", 
                            "flux_units": "1", 
                            "instrument_value": "160", 
                            "limiting_flux": "19.22", 
                            "obsdate": "2026-01-11.22008", 
                            "observer": "Robot"
                        }
                    }
                }, 
                "proprietary_period": {
                    "proprietary_period_units": "days", 
                    "proprietary_period_value": "0"
                }, 
                "proprietary_period_groups": [
                    "18"
                ], 
                "ra": {
                    "value": "7.582516"
                }, 
                "reporter": "J. Tonry, L. Denneau, H. Weiland (IfA, University of Hawaii), N. Erasmus, W. Koorts (South African Astronomical Observatory), A. Jordan, V. Suc (UAI, Obstech), M. R. Alarc\u00f3n, J. Licandro, P. Nichita (IAC), S. J. Smartt, K. W. Smith (Oxford/QUB), D. R. Young, M. Nicholl, M. Fulton, M. McCollum, T. Moore, J. Weston, X. Sheng, C. R. Angus, A. Wilson, A. Aamer, D. Magill, P. J. Broda, A. J. Smith (QUB), P. Ramsden (Birmingham/QUB), L. Shingles (GSI/QUB), S. Srivastav, J. H. Gillanders, H. Stevance, A. J. Cooper, F. Stoppa, J. Tweddle, L. Eastman (Oxford), L. Rhodes (TSI/McGill), A. Rest (STScI), T.-W. Chen (NCU), C. Stubbs (Harvard), J. S. Sommer (LMU), B. P. Schmidt (ANU)", 
                "reporting_group_id": "18"           
            }
        }
    }


Here is example data we get back from TNS after reporting ( when doing the ``getBulkReportReply`` )

.. code-block:: json

    {
        "data": {
            "feedback": {
                "at_report": [
                    {
                        "100": {
                            "message": "Transient object was inserted.", 
                            "message_id": 100, 
                            "objname": "2026ob"
                        }, 
                        "internal_ids": {
                            "internal_name": "ATLAS26afg", 
                            "internal_objid": "1003019830331501200"
                        }
                    }
                ]
            }
        }, 
        "id_code": 200, 
        "id_message": "OK"
    }
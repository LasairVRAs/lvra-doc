Quick Start
============

What is the LVRA?
------------------------------------------

**The Lasair VRAs help rank your alert stream**. 
In the context of Lasair it is an annotator which adds a **classification** and **supplementary features** that can be used for **filtering and prioritising Rubin alerts**. I show you how below. 

*Why is it called a "Virtual Research Assistant"?* Because my pipelines, bots and models are heavily inspired by the way researchers think through a decision. The actual model and what it ranks will vary depending on the stream and the 
needs, but the ethos is the same: What would a human do? What does a human need? 

**These are not Agentic AI**. 
I train "old fashioned" agorithms on real data from a telescope stream.
If you want to see the work I did for the  `ATLAS Virtual Research Assistant, see Stevance et al. 2025 <https://arxiv.org/abs/2506.09778>`_.
A paper is in the works for the LVRA. 


Worht noting is that I am an extra-galactic transient astronomer looking for supernovae and other distant explosions. 
If you are an AGN, CV or Solar System Person, take what I do with a pinch of salt (e.g. when 
my algorithms classify something as ``AGN`` or ``mover``).


Use it in your filters
---------------------------

If you don't already know what a Lasair filter is, check the `Lasair documentation <https://lasair-lsst.readthedocs.io/en/develop/core_functions/make_filter.html#make-a-lasair-filter>`_.



Step 1: Make sure you have selected the annotator 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
On the filter page go to the ``Object Annotators`` drop down menu and select the ``LVRA``, as shown in the images. 


.. image:: _static/img/lvra-quickstart/deselected_annotator.png          
    :width: 390                                                                
    :align: left  

.. image:: _static/img/lvra-quickstart/selected_annotator.png          
    :width: 400                                                                
    :align: right

If you don't do this, your filter will not work, and when you write your filter the syntax helper of the Lasair front pages 
will also not autocomplete properly.

Step 2: Writing a simple filter query
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are two places that you might use the LVRA: The ``SELECT COLUMNS`` (what data you want to get) and the ``WHERE`` statment (what constraints you want to impose).

This would return only the ``diaObjectId`` and the LVRA score given to that object.

.. code-block:: sql

   -- SELECT block
   objects.diaObjectId,  
   LVRA.classification



This would select only the alerts with LVRA score greater than 0.9.

.. code-block:: sql

   -- WHERE block
   LVRA.classification>0.9

.. note ::
    The LVRA score stored in the annotation ``classification`` is the extragalactic score given by our Champion model. 



Step 2 but better: Advanced filter query
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The LVRA annotator also provides a whole host of additional features and scores via the annotator's dictionary 
(scroll down for a table of the full list of fields in the dictionary). 
To invoke them in your filters you need to use the ``JSON_EXTRACT`` function.

For example in this ``SELECT`` block I added the following columns:

* ``current_snr`` : The signal to noise ratio of the ``diaSourceId`` that caused this particular alert
* ``n_loR_sources``: The number of ``diaSourceId`` with Rubin reliability < 0.5 in this lightcurve
* ``n_hiR_sources``: The number of ``diaSourceId`` with Rubin reliability > 0.5 in this lightcurve
* ``first_gt21``: A flag which is set to ``1`` if it is the first time an object has reached 21st magnitude
* ``delta_days_total``: The number of days since the first point in the lightcurve.

.. code-block:: sql

   -- SELECT block
   objects.diaObjectId,  
   LVRA.classification,
   JSON_EXTRACT(LVRA.classdict, "$.current_snr") as snr,
   JSON_EXTRACT(LVRA.classdict, "$.n_loR_sources") as N_lo, 
   JSON_EXTRACT(LVRA.classdict, "$.n_hiR_sources") as N_hi, 
   JSON_EXTRACT(LVRA.classdict, "$.first_gt21") as lvra_first_time_brighter_21mag,
   JSON_EXTRACT(LVRA.classdict, "$.delta_days_total") as lvra_delta_days
   


In the following ``WHERE`` statement, instead of selecting the alerts by their raw extragalactic score, we 
instead exclude alerts that are likely to be ``movers`` or ``bogus``. We also select alerts that 
have at least 4 ``diaSourceId`` with reliability score greater than 0.5, and we 
only include lightcurves that have been going for 30 days. 


.. code-block:: sql

   -- WHERE block
   JSON_EXTRACT(LVRA.classdict, "$.champion.bogus") < 0.1
   AND JSON_EXTRACT(LVRA.classdict, "$.champion.mover") < 0.1
   AND JSON_EXTRACT(LVRA.classdict, "$.n_hiR_sources") > 4
   AND JSON_EXTRACT(LVRA.classdict, "$.delta_days_total") > 30


.. warning::
    If the there is a typo in the "$.myfeature.example" part of the query, the filter **fails silently**. 
    It just assumes the field doesn't exist or is empty. ``JSON_EXTRACT(LVRA.classdict, "$.champino.bogus") < 0.1``
    will ALWAYS be false so your filter will return nothing.
    **Check and double check the filter is doing what you want before saving.**


Step 3: Saving the filter CORRECTLY
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you're happy with your filter you need to save it correctly - wheter you want an email digest or a kafka stream you need to trigger
on new annotation. Let me say it again:

.. important::
    You need to filter **On new annotation**


.. figure:: _static/img/lvra-quickstart/filter_settings_on_annotation.png    
    :width: 400                                                               
    :align: Center



The Triggers are the events that add an object to your queue.

When you select ``On new annotation`` an alert will be added to your filter queue **as soon as my LVRA annotation has been received by Lasair**.

If you select ``On new alert``, my annotation and scores will go in, and **next time this object gets an alert** Lasair will
check the LVRA score and other features against your filter. You will get the object in your queur one alert later. 

*What if I select both?* - I don't know, I've not tested that yet. I guess you'll get both the correct and the incorrect version. 



Labels and what they mean 
--------------------------
The LVRA scores the alerts in the following categories (all run from 0 to 1, and they overall sum to 1 for a given object):

* ``extragalactic``: An extragalactic transient (but not an AGN)
* ``mover``: Suspected mover
* ``bogus``: Not a real astrophysical event
* ``agn``: Suspect AGN activity
* ``real``: Probably real but not an obvious extragalactic transient (or other)
* ``gal``: [NOT USED YET]. Suspected galactic event, e.g. variable star, CV. 


The ``classficiation`` value in the LVRA annotator is the ``extragalactic`` score, and the simplest thing
is to filter and rank your stream based on that. 

You might find that you can combine the scores of different categories to get to a better bespoke filter that 
suits your needs, so all the scores are given in the annotator's dictionary. 


Annotator Dictionary
---------------------------

Here is the list of features and additional scores you can access through the ``JSON_EXTRACT`` function. 

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Public name
     - What it is
   * - ``blame_diaSourceId``
     - The source (latest alert) the scores and features were computed for
   * - ``champion`` / ``challenger`` / ``retired``
     - ``{"version": ..., "extragal": ..., "mover": ..., "real": ..., "bogus": ..., "agn": ...}``, or ``null`` if the role is empty
   * - ``n_loR_sources``
     - Number of sources with R < 0.5
   * - ``n_hiR_sources``
     - Number of sources with R > 0.5
   * - ``n_gtXX``
     - Number of detections brighter than XX mag
   * - ``ever_gtXX``
     - Has the transient ever been brighter than XX mag
   * - ``first_gtXX``
     - Is this the first time it is brighter than XX mag
   * - ``max_flux``
     - Maximum flux (nJy)
   * - ``delta_days_since_max``
     - Days since the maximum (0 if the latest detection is the max)
   * - ``delta_days_to_max``
     - Days from ``firstDiaSourceMjdTai`` to the maximum
   * - ``delta_days_total``
     - Days from ``firstDiaSourceMjdTai`` to the latest detection
   * - ``current_snr``
     - SNR of the latest detection
   * - ``n_det_{b}``
     - Number of detections in band b (u, g, r, i, z, y). e.g. ``net_det_y``
   * - ``n_det_snr10_{b}``
     - Number of detections with SNR > 10 in band b. e.g. ``net_det_snr10_y``



FAQ
------------------

* `When I go to the LVRA annotator page there is a whole bunch of \*\*\*\* - what's going on?`

I you go straight to the `LVRA annotator page <https://lasair.lsst.ac.uk/annotators/LVRA/>`_ you will see 
all the annotations give recently **unordered**. You can click on the ``classification`` column to order the table. 


* *What is a Champion/Challenger/Retired model?*

The Champion model is the currently preffered (best) model, as decreed by `me`. 
The Challenger model is a model I am trying against the current benchmark (Champion), if I find it performs 
better than the Champion I will update the annotator. 
The old Champion model will then become "Retired" and for a time I will keep scoring with the old model
so that people that rely on its values can keep using it.

* *When/How will you announce a change in model version?*

The current plan is to do this via the Lasair blog topic on the Rubin Community Forum

* *What about r0b?*

``r0b``, my "real or bogus" prototype is currently still active at the ``r0b-lvra`` annotator. 
**It will be retired in January 2027**. It was always a prototype LVRA, and with all the lessons learned
in Spring/Summer 2026 we can move to a long term version of the annotator. 
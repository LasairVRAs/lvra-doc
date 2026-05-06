r0b: Real Or Bogus
=====================

.. caution::
    I am actively working on this algorithm - and significant updates will be put in production throughout begining of LSST operations (which have not started yet). 

The `reliability score provided by Rubin <https://prompt-products.lsst.io/processing/filtering/index.html>`_ is very useful for first cuts but as a transient astronomer it is not sufficient
to create a clean enough stream. 
By using the reliability score alongside other features in the alert packet we can make better decisions. 
This work is based on the `ATLAS Virtual Research Assistant (Stevance et al. 2025) <https://arxiv.org/abs/2506.09778>`_, and adds
methods of Active Learning so I can train directly on the stream.


Because I am training **directly on the live Rubin stream** it will take a few weeks to train and verify an algorithm. The details of this will be 
added to this documentation and make the object of a proper paper later in the year. If you have questions in the mean-time email me or start a topic
on the `Lasair Community Forum <https://community.lsst.org/c/support/support-lasair/55>`_. 


The ``r0b`` LVRA is a binary classifier **downstream** of a filter that makes preliminary cuts: 

    - ``reliability`` >0.5  
    - ``SHERLOCK`` label either ``SN``, ``NT``, ``ORPHAN`` or ``UNCLEAR``.
    - ``nDiaSources`` >= 2
    
.. warning:: 
    The r0b scores are **absolutely not suitable for Solar System Objects of AGNs**. If they work well, it is on accident. Use at your own peril. 

What is in the r0b annotator and how to use it?
------------------------------------------------

The r0b score
~~~~~~~~~~~~~~~

The score given by the annotator ranges between 0 (bogus) and 1 (real). 
The score is given **to a given SOURCE (lightcurve point) not to a given OBJECT (transient)**.
So if a supernova is fading and the alerts have get lower SNR they may no longer get a good 
r0b score. Giving scores to objects as a whole or providing additional information in the 
dictionary so you can make more nuanced queries is on the to-do list. 

Preliminary analysis of r0b in the stream shows that for scores ``>0.75``, the 
**purity of real extragalactic transients** is around 80% (60% if you ordered by reliability score). 
The main contaminants are AGNs. 
For lower thresholds, r0b scores and reliability scores have similar purity but the mixture
of contaminants is different. 

To use the r0b score you need to select the ``r0b_lvra`` annotator in your filter (there is a drop down menu).
And then you can add a line in your filter criteria like:

.. code-block:: sql

    r0b_lvra.classification > 0.9

 

Additional features you can query on
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Although the current version of r0b only uses the Lasair filter columns and the lightcurve features associated with the latest point to calculate a score, 
the annotator is build to provide additional flags and information that is not otherwise available in the Lasair filters. 

Namely:

- **n_gtXX** (e.g. n_gt22): The number of lightcurve points with magnitude BIRGHTER than 22nd, 21st, 20th, 19th or 18th magnitude. 
- **brighterXX** (e.g. brighter22): A boolean flag indicating whether there is at least one point brighter than 22nd, 21st, 20th, 19th or 18th magnitude.
- **firstXX** (e.g. first22): A boolean flag indicating whether this is the first time the transient has crossed a given magnitude threshold_flags_provenance

If you want to use these in your query you can add a line like:

.. code-block:: sql

    AND JSON_EXTRACT(r0b_lvra.classdict, "$.n_gt22") > 4

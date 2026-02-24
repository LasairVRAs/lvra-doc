r0b: Real Or Bogus
=====================

.. caution::
    I am actively working on this algorithm - and significant updates will be put in production **throughout March 2026 at least**. 

The `reliability score provided by Rubin <https://prompt-products.lsst.io/processing/filtering/index.html>`_ is very useful for first cuts but as a transient astronomer it is not sufficient
to create a clean enough stream. 
By using the reliability score alongside other features in the alert packet we can make better decisions. 
This work is based on the `ATLAS Virtual Research Assistant (Stevance et al. 2025) <https://arxiv.org/abs/2506.09778>`_, and adds
methods of Active Learning so I can train directly on the stream.


Because I am training **directly on the live Rubin stream** it will take a few weeks to train and verify an algorithm. The details of this will be 
added to this documentation and make the object of a proper paper later in the year. If you have questions in the mean-time email me or start a topic
on the `Lasair Community Forum <https://community.lsst.org/c/support/support-lasair/55>`_. 



The ``r0b`` LVRA is a binary classifier **downstream** of a filter that makes preliminary cuts: 
*  ``reliability`` >0.5  
*  ``SHERLOCK`` label either ``SN``, ``NT``, ``ORPHAN`` or ``UNCLEAR``.
*  ``nDiaSources``` >= 2
*  


.. warning:: 
    The r0b scores are **absolutely not suitable for Solar System Objects of AGNs**. If they work well, it is on accident. Use at your own peril. 

How does it work? What data was it trained on? Performance?
-------------------------------------------------------------
*Come back in March/April 2026*
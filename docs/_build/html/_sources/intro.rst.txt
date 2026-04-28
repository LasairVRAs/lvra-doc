Introduction
=================

Welcome to the documentation for the Lasair Virtual Research Assistants (VRAs), machine learning algorithms that will provide further annotation 
to the LSST stream on the Lasair platform. 

I am an extra-galactic transient astronomer looking for supernovae and other distant explosions.

.. important::
    These algorithms are trained directly on the live Rubin stream, using human-made labels provided via eyeballing. Because I am the eyeballer, my 
    scientific biases can affect the performance of the tools I build. If you are an AGN, CV or Solar System Person, take what I do with a pinch of salt. 
    I will always welcome your feedback as well, feel free to email me. 


What is a "Virtual Research Assistant"?
------------------------------------------
They're just my bots that I train myself on bespoke astronomical data;  **they are not Agentic AI**. 
If you want to see the work I did for the  `ATLAS Virtual Research Assistant, see Stevance et al. 2025 <https://arxiv.org/abs/2506.09778>`_

.. note::
    My methods use Feature based ML, **exclusively trained on real data**, and as of recently focus on using Active Learning methods so I can train directly on Rubin 
    as a sole eyeballer (they allow me to train algos with a few hundred examples instead of thousands or millions).

If you see something tagged **VRA** or **LVRA**, it's probably something I made and if you need someone to blame it will likely be me. 
I give them human-like names with ``l33t``-like formatting, which is another way to recognise them. 

The first Lasair VRA is ``r0b``, my real-or-bogus classifier to help me find real extra-galactic events. More docs to in the next few weeks. 




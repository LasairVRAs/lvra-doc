Dev Notes
==========

Training Check-list
---------------------

1. rsync the feature csv files from the remote server to local

.. code-block:: bash
    rsync -avz -e "ssh -i ~/.ssh/id_oxservers" lasair@oxdb1:/home/lasair/data/vra_data/csv/ .

2. Update the training pool

.. code-block:: bash
    conda activate lvra
    cd ~/software/lvra/lvra/training
    python ./make_pool.py 



testing my  template
----------------------

some code: ``code``

.. code-block:: python

    import lasair

.. warning:: 
    test

.. note::
    test

.. tip::
    test

.. caution::
    test

.. important::
    test

.. error::
    bla
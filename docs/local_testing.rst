Local Testing Procedure
==========================

Feature making 
---------------

Make sure the sqlite database contains the right tables (see infrastructure set up), and 
make sure that our test stem is in there and its `r0b` column is set to 0:

.. code-clock:: sql

    insert into feature_making (stem, r0b) values ('20260202_102448', 0) on conflict (stem) do update set r0b=excluded.r0b;



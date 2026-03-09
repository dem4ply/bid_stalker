===========
bid_stalker
===========


.. image:: https://img.shields.io/pypi/v/bid_stalker.svg
        :target: https://pypi.python.org/pypi/bid_stalker

.. image:: https://readthedocs.org/projects/bid-stalker/badge/?version=latest
        :target: https://bid-stalker.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Scrapper for bids online


* Free software: WTFPL
* Documentation: https://bid-stalker.readthedocs.io.


**********
how to use
**********

.. code-block:: bash

	# check config and if index are created
	bid_stalker elastic
	# create the index
	bid_stalker elastic create
	# print audictions for country
	bid_stalker bidspotter mexico
	# send the audictions to elasticsearch
	bid_stalker bidspotter mexico --to_elastic
	# list audictions from elasticsearch
	bid_stalker elastic list
	#scan missing articles of a auction
	bid_stalker elastic scan --missing --pk=-rGFupwBf5atcTatMyOS



Features
--------

* TODO

Pockels Modulator Mask
========================

Getting Started
-------------------

Dependencies
~~~~~~~~~~~~~~~~
This requires python (I recommend installing via `miniconda <https://conda.io/projects/conda/en/latest/user-guide/install/index.html>`_), numpy (which is bundled in miniconda), and `gdspy <https://github.com/heitzmann/gdspy>`_

To generate the full mask, run the following:

.. code-block::

    python pockels_modulator_mask.py


(TODO) Changes in v 2.0:

	- Added smaller devices around the main 2mm diameter device
	- Increased size of bond pads
	- Increased number of bond pads
	- Moved bond pads a little further away from structures
	- Added aml-bonder alignment marks on one layer
	- Added inverted ASML alignment marks

Version 1.0 contains:

	- 2 main layers: mesas and metal contacts
	- Single device per die of 2mm diameter
	- 

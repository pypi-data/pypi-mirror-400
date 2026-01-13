DTMF Table - Python Documentation
===================================

A zero-heap, ``no_std`` friendly, **const-first** implementation of the standard DTMF (Dual-Tone Multi-Frequency) keypad used in telephony systems.

This Python package provides compile-time safe mappings between keypad keys and their canonical low/high frequencies, along with **runtime helpers** for practical audio processing. Built with Rust for performance and safety.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api

Features
--------

- **Const-evaluated forward and reverse mappings** between DTMF keys and frequencies
- **Closed enum for keys** — invalid keys are unrepresentable
- **Zero allocations** in the underlying Rust implementation
- Runtime helpers:
   - Tolerance-based reverse lookup (e.g., from FFT peaks)
   - Nearest snapping for noisy frequency estimates
   - Iteration over all tones and keys

Installation
------------

.. code-block:: bash

   pip install dtmf-table

Quick Example
-------------

.. code-block:: python

   from dtmf_table import DtmfTable, DtmfKey

   # Construct a table instance
   table = DtmfTable()

   # Forward lookup from key to canonical frequencies
   key = DtmfKey.from_char('8')
   low, high = key.freqs()
   assert (low, high) == (852, 1336)

   # Reverse lookup with tolerance (e.g., from FFT bin centres)
   key = table.from_pair_tol_f64(770.2, 1335.6, 6.0)
   assert key.to_char() == '5'

   # Nearest snapping for noisy estimates
   key, snapped_low, snapped_high = table.nearest_u32(768, 1342)
   assert key.to_char() == '5'
   assert (snapped_low, snapped_high) == (770, 1336)

DTMF Frequency Table
--------------------

The library provides access to all 16 standard DTMF frequencies:

+--------+--------+--------+--------+--------+
|        | 1209Hz | 1336Hz | 1477Hz | 1633Hz |
+========+========+========+========+========+
| 697Hz  |    1   |    2   |    3   |    A   |
+--------+--------+--------+--------+--------+
| 770Hz  |    4   |    5   |    6   |    B   |
+--------+--------+--------+--------+--------+
| 852Hz  |    7   |    8   |    9   |    C   |
+--------+--------+--------+--------+--------+
| 941Hz  |    *   |    0   |    #   |    D   |
+--------+--------+--------+--------+--------+

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
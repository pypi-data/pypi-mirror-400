
WuttaPOS
========

This is an old idea but a new effort, for a Python-based point of sale system.

This project includes two primary components:

- web app and related daemons, to run on the server
- standalone GUI app, to run on the lanes

This project is in the very early stages and is not yet documented.
It is based on an earlier effort, which used Rattail:
`rattail/wuttapos`_

.. _rattail/wuttapos: https://forgejo.wuttaproject.org/rattail/wuttapos

However this project uses `Wutta Framework
<https://wuttaproject.org>`_, has no Rattail dependencies, and "starts
over" for (mostly) everything.


.. toctree::
   :maxdepth: 2
   :caption: Documentation

   narr/install

.. toctree::
   :maxdepth: 1
   :caption: Package API

   api/wuttapos
   api/wuttapos.server
   api/wuttapos.terminal

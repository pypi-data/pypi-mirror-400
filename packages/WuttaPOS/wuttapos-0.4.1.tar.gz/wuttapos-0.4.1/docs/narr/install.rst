
==============
 Installation
==============

For now this only describes a *development* setup, which assumes the following:

* Linux OS
* Python 3.11 or newer
* database in PostgreSQL or MySQL

These steps will setup both the Server and Terminal in a shared
virtual environment.


Virtual Environment
-------------------

Obviously you should make a virtual environment.

.. code-block:: sh

   python3 -m venv wuttapos
   cd wuttapos
   source bin/activate


Install Package
---------------

Install the WuttaPOS package within your virtual environment:

.. code-block:: sh

   bin/pip install WuttaPOS


Install Server
--------------

**Please note, you must create your database before running the installer.**

Run the WuttaPOS installer to setup the Server app:

.. code-block:: ini

   bin/wuttapos install

Now you can run the Server app via command line:

.. code-block:: ini

   bin/wutta -c app/web.conf webapp -r

And browse it (by default) at http://localhost:9080

The first time you browse to it, you must enter details for the
(first) admin user.  That can all be changed later, just needs an
account to get things started.

After that you must login using the credentials you gave it.

At this point the app is fully functional.

Don't forget you can "become root" (via user menu in top right of
screen) to bypass all permission checks.  This shows all menu options,
tool buttons etc. no matter what your normal permissions are.
(Only users in the Administrator role can become root.)


Sample Data
~~~~~~~~~~~

You may also want to install sample data, to get some basic tables
populated and avoid that headache.  As of now the sample data is very
minimal, and obviously not "real" so it's only a small convenience.

To install sample data, first "become root" (via user menu in top
right of screen) and then go to Admin -> App Info and click Install
Sample Data.

Eventually the sample data, and/or data import options in general,
should be improved - but that will come later.


Install Terminal
----------------

**Please note, this assumes you already installed the Server as described above.**

For now, we'll just install the Terminal alongside the Server.  They
will share the same virtual environment, installed code, app database,
and "most of" the config files.

So within your virtual environment, run the same installer again:

.. code-block:: ini

   bin/wuttapos install

.. note::

   You will be asked for store and terminal IDs - these should be
   valid and refer to actual records for those types, within the
   database.  See the Admin menu of the Server web app to manage those
   records.

At this point the Terminal app should be ready to go.  To run the
standalone GUI:

.. code-block:: sh

   bin/wuttapos -c app/terminal.conf run

You will need to login; the POS uses a special set of permissions but
the first admin user should already have all that are needed.  So just
login using same credentials as for the Server app.

It's also possible (due to the magic of Flet/Flutter) to *serve* the
Terminal as a web app:

.. code-block:: sh

   bin/wuttapos -c app/terminal.conf serve

In that case (by default) you can browse it at http://localhost:8332

That might be useful for online demo purposes etc. but definitely the
intention is to run as standalone GUI for production.  (However the
story around tablets is TBD.)

For now, running as a web service like that is not a supported
feature.

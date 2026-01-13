
==============
 Installation
==============

For now this only describes a *development* setup, which assumes the following:

* Linux OS
* Python 3.11 or newer
* database in PostgreSQL or MySQL

These steps will setup both the server and terminal in a shared
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

Run the WuttaPOS installer to setup the server app:

.. code-block:: ini

   bin/wuttapos install

Now you can run the server app via command line:

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

TODO: this is not yet documented

Introduction
============

Installation
------------
AnTrak relies on PostgreSQL and PostGIS extension.

Database initialization::

    # createdb antrak
    # psql -f /usr/share/postgresql/contrib/postgis-2.1/spatial_ref_sys.sql antrak
    # ./db/create antrak

.. vim: sw=4:et:ai

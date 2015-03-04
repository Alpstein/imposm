Imposm is an importer for OpenStreetMap data. It reads XML and PBF files and
can import the data into PostgreSQL/PostGIS databases.

It is designed to create databases that are optimized for rendering/WMS
services.

It is developed and supported by `Omniscale <http://omniscale.com>`_, runs on
Linux or Mac OS X and is released as open source under the `Apache Software
License 2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>`_.

See http://imposm.org/ for more information.


This fork extends the original `imposm` by

* possibility to import route relations

(From https://github.com/omniscale/imposm/pull/34)

The changes are inspired by those published by `michalmacki <https://bitbucket.org/michalmacki/imposm-routes/>`_.
As those seem to be based on an outdated imposm, they are contained in an hg
repository instead of git, and I saw the need for some slight changes (most
notably support of routes in the ContainsRelationBuilder, not just
UnionRelationBuilder), I replicated several of his changes.

Imposm is an importer for OpenStreetMap data. It reads XML and PBF files and
can import the data into PostgreSQL/PostGIS databases.

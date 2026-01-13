.. -*- coding: utf-8 -*-
.. :Project:   metapensiero.sqlalchemy.dbloady -- Generic FK test notes
.. :Created:   lun 07 nov 2016 10:16:32 CET
.. :Author:    Lele Gaifax <lele@metapensiero.it>
.. :License:   GNU General Public License version 3 or later
.. :Copyright: © 2016 Lele Gaifax
..

=======================
 Generic FK test notes
=======================

This checks the loader ability of dealing with the particular `generic foreign keys`__ trick I
used in a couple of projects, in particular with regards to the custom comparator needed to
verify if an instance already exists in the database.

__ http://docs.sqlalchemy.org/en/latest/_modules/examples/generic_associations/generic_fk.html

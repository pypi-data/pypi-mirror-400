.. -*- coding: utf-8 -*-
.. :Project:   metapensiero.sqlalchemy.dbloady -- Non-relationship attributes test notes
.. :Created:   lun 07 nov 2016 10:31:57 CET
.. :Author:    Lele Gaifax <lele@metapensiero.it>
.. :License:   GNU General Public License version 3 or later
.. :Copyright: © 2016, 2017 Lele Gaifax
..

========================================
 Non-relationship attributes test notes
========================================

Tests whether the loader is able to deal with *non-relationship attribute assignments*, that is
when a plain attribute gets assigned with an *instance*: the primary key of the instance should
be assigned instead.

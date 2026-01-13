.. -*- coding: utf-8 -*-
.. :Project:   metapensiero.sqlalchemy.dbloady -- Adaptor test notes
.. :Created:   lun 07 nov 2016 09:56:04 CET
.. :Author:    Lele Gaifax <lele@metapensiero.it>
.. :License:   GNU General Public License version 3 or later
.. :Copyright: © 2016 Lele Gaifax
..

====================
 Adaptor test notes
====================

This test exercise the ability to hook a custom *adaptor* into the load process, that gets
called on each *record*\ 's data just before it gets assigned to the instance. The hooked
function may deliberately change the incoming data, returning a new dictionary that will
eventually used to update the instance.

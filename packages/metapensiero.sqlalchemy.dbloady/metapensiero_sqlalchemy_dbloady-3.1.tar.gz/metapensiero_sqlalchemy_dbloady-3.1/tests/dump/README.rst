.. -*- coding: utf-8 -*-
.. :Project:   metapensiero.sqlalchemy.dbloady -- Dump test notes
.. :Created:   lun 07 nov 2016 10:05:33 CET
.. :Author:    Lele Gaifax <lele@metapensiero.it>
.. :License:   GNU General Public License version 3 or later
.. :Copyright: © 2016 Lele Gaifax
..

=================
 Dump test notes
=================

This exercises the ``dbdumpy`` tool, verifying that its output corresponds to the expected one:
a test database is created and populated with some content, then it gets dumped using the
tool. The result is used to create a second test database, and eventually the test compares the
backups of the two databases.

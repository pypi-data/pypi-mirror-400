.. -*- coding: utf-8 -*-
.. :Project:   metapensiero.sqlalchemy.dbloady -- Preload test notes
.. :Created:   lun 07 nov 2016 10:24:38 CET
.. :Author:    Lele Gaifax <lele@metapensiero.it>
.. :License:   GNU General Public License version 3 or later
.. :Copyright: © 2016 Lele Gaifax
..

====================
 Preload test notes
====================

This test exercises the *preload* feature, where a custom setup is executed before loading the
YAML dump: in the specific case, the setup installs a special *constructor* and an *implicit
resolver* into the ``pyyaml`` library so that it can recognize particular *time of the day*
values.

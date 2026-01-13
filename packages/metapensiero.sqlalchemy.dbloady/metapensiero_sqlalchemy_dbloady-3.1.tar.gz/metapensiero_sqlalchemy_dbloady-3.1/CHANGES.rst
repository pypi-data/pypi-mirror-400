.. -*- coding: utf-8 -*-

Changes
-------

3.1 (2026-01-06)
~~~~~~~~~~~~~~~~

- Fix compatibility with ``ruamel.yaml`` 0.19+

- Test against 3.13 and Python 3.14


3.0 (2024-12-29)
~~~~~~~~~~~~~~~~

- Expose a function to build the Python package in the flake


3.0.dev6 (2024-11-26)
~~~~~~~~~~~~~~~~~~~~~

- Use the correct name to expose the package in the flake


3.0.dev5 (2024-11-26)
~~~~~~~~~~~~~~~~~~~~~

- Stop testing against ``SQLAlchemy`` 1.4, use only the version coming with Nixpkgs


3.0.dev4 (2024-11-26)
~~~~~~~~~~~~~~~~~~~~~

- Fix compatibility with recent ``ruamel.yaml``

- Upgrade tested versions of ``SQLAlchemy``

- Test and expose packages for Python 3.11 and Python 3.12


3.0.dev3 (2023-06-11)
~~~~~~~~~~~~~~~~~~~~~

- Drop support for ``SQLAlchemy`` 1.3.x in the test suite, exercise them against 1.4.x and 2.0.x,
  under both Python 3.10 and Python 3.11: note that this does not necessarily mean that the
  library won't work with Python 3.9 and SA 1.3.x


3.0.dev2 (2022-10-20)
~~~~~~~~~~~~~~~~~~~~~

- Fix compatibility with ``SQLAlchemy`` 2


3.0.dev1 (2022-07-22)
~~~~~~~~~~~~~~~~~~~~~

- Rewrite packaging with :PEP:`621`, replacing setup.py with pyproject.toml

- Use a Nix__ flake instead of a plain virtualenv to create the development environment

  __ https://nixos.org/guides/how-nix-works.html
  _
- Use just__ instead of ``make`` for development tasks

  __ https://just.systems


3.0.dev0 (2021-10-17)
~~~~~~~~~~~~~~~~~~~~~

- Target Python 3.9+


2.10 (2020-01-18)
~~~~~~~~~~~~~~~~~

- Fix an issue with loading many-to-many relationships


2.9 (2019-06-24)
~~~~~~~~~~~~~~~~

- Mimic how PostgreSQL decodes ``\N`` as ``None`` in the TSV tag


2.8 (2019-06-24)
~~~~~~~~~~~~~~~~

- Ability to load data from an external tab-separated-values file


2.7 (2019-05-10)
~~~~~~~~~~~~~~~~

- Emit a critical log on attribute assignment failure, to aid debugging bad input


2.6 (2018-04-17)
~~~~~~~~~~~~~~~~

- Remove the fixup to progressbar2 `issue #162`__, solved in its 3.7.1 release

__  https://github.com/WoLpH/python-progressbar/issues/162


2.5 (2018-04-09)
~~~~~~~~~~~~~~~~

- Try to fix different behaviour in progressbar2 3.7.0 w.r.t. multiple progress bars


2.4 (2018-04-08)
~~~~~~~~~~~~~~~~

- Now File elements can read text files

- Support dumping hstore values (not tested enough, though)


2.3 (2017-06-07)
~~~~~~~~~~~~~~~~

- Fix handling of property based attributes


2.2 (2017-05-18)
~~~~~~~~~~~~~~~~

- The File elements may now contain their content, without accessing external files


2.1 (2017-05-02)
~~~~~~~~~~~~~~~~

- New ``--quiet`` option to omit the progress bar


2.0 (2017-04-06)
~~~~~~~~~~~~~~~~

- Require `ruamel.yaml`__ instead of PyYAML__

__ https://pypi.python.org/pypi/ruamel.yaml
__ https://pypi.python.org/pypi/PyYAML


1.11 (2017-03-22)
~~~~~~~~~~~~~~~~~

- Spring cleanup, no externally visible changes


1.10 (2016-11-16)
~~~~~~~~~~~~~~~~~

- Reduce load noise by using progressbar2__

__ https://pypi.python.org/pypi/progressbar2


1.9 (2016-11-15)
~~~~~~~~~~~~~~~~

- Ability to execute raw SQL statements to fetch a value from the database


1.8 (2016-11-15)
~~~~~~~~~~~~~~~~

- Better tests

- Handle assignments to non-relationship properties


1.7 (2016-11-05)
~~~~~~~~~~~~~~~~

- Make Python 3 happy by explicitly use binary mode to read external files


1.6 (2016-10-29)
~~~~~~~~~~~~~~~~

- Quick&approximated solution to load `generic associations`__

__ http://docs.sqlalchemy.org/en/latest/_modules/examples/generic_associations/generic_fk.html


1.5 (2016-03-12)
~~~~~~~~~~~~~~~~

- New complementary dump functionality, exposed by a new cli tool, dbdumpy

- Cosmetic, backward compatible, changes to the YAML format, for nicer sorting


1.4 (2016-02-10)
~~~~~~~~~~~~~~~~

- Data files and preload/postload scripts may be specified also as package relative resources


1.3 (2016-01-14)
~~~~~~~~~~~~~~~~

- New --preload and --postload options to execute arbitrary Python scripts before or after the
  load


1.2 (2016-01-09)
~~~~~~~~~~~~~~~~

- Fix source distribution


1.1 (2016-01-09)
~~~~~~~~~~~~~~~~

- Fix data refs when loading from compact representation


1.0 (2016-01-07)
~~~~~~~~~~~~~~~~

- Allow more compact representation when all instances share the same fields

- Extract dbloady from metapensiero.sphinx.patchdb 1.4.2 into a standalone package

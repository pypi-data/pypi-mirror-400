.. -*- coding: utf-8 -*-
.. :Project:   metapensiero.sqlalchemy.dbloady -- YAML based data loader
.. :Created:   ven  1 gen 2016, 16.19.54, CET
.. :Author:    Lele Gaifax <lele@metapensiero.it>
.. :License:   GNU General Public License version 3 or later
.. :Copyright: © 2016, 2017, 2019 Lele Gaifax
..

=================================
 metapensiero.sqlalchemy.dbloady
=================================

----------------------
YAML based data loader
----------------------

 :author: Lele Gaifax
 :contact: lele@metapensiero.it
 :license: GNU General Public License version 3 or later

.. contents::

Data loader
===========

Load new instances in the database, or update/delete existing ones, given a data structure
represented by a YAML stream, as the following::

    - entity: gam.model.Fascicolo
      key: descrizione
      # no data, just "declare" the entity

    - entity: gam.model.TipologiaFornitore
      key: tipologiafornitore
      rows:
        - &tf_onesto
          tipologiafornitore: Test fornitori onesti

    - entity: gam.model.ClienteFornitore
      key: descrizione
      rows:
        - descrizione: Test altro fornitore onesto
          tipologiafornitore: *tf_onesto
          partitaiva: 01234567890
        - &cf_lele
          codicefiscale: GFSMNL68C18H612V
          descrizione: Dipendente A

    - entity: gam.model.Dipendente
      key: codicefiscale
      rows:
        - &lele
          codicefiscale: GFSMNL68C18H612V
          nome: Emanuele
          cognome: Gaifas
          clientefornitore: *cf_lele
          foto: !File {path: ../img/lele.jpg}

    - entity: gam.model.Attrezzature
      key: descrizione
      rows:
        - &macchina
          descrizione: Fiat 500
          foto: !File
            compressor: lzma
            content: !!binary |
              /Td6WFoAAATm1rRGAgAhA...

    - entity: gam.model.Prestiti
      key:
        - dipendente
        - attrezzatura
      rows:
        - dipendente: *lele
          attrezzatura: *macchina

As you can see, the YAML document is a sequence of entries, each one defining the content of a
set of *instances* of a particular *entity*.

The ``entity`` must be the fully qualified dotted name of the SQLAlchemy mapped class.

The ``key`` entry may be either a single attribute name or a list of them, not necessarily
corresponding to the primary key of the entity, provided that it uniquely identifies a single
instance.  To handle the simplest case of structured values (for example, when a field is
backed by a PostgreSQL HSTORE), the key attribute name may be in the form ``name->slot``::

    - entity: model.Product
      key: description->en
      rows:
        - &cage
          description:
            en: "Roadrunner cage"
            it: "Gabbia per struzzi"

The ``rows`` (or ``data``) may be either a single item or a list of them, each containing
the data of a single instance, usually a dictionary.

.. _fields:

When all (or most of) the instances share the same fields, a more compact representation may be
used::

    - entity: model.Values
      key:
        - product
        - attribute
      fields: [ product, attribute, value ]
      rows:
        - [ *cage, *size, 110cm x 110cm x 120cm ]
        - [ *cage, *weight, 230kg ]

where ``fields`` contains a list of field names and ``rows`` is a sequence of lists, each
containing the values of a single instance.  The two sintaxes may be mixed though, so you can
say::

    - entity: model.Person
      key: [ lastname, firstname ]
      fields: [ lastname, firstname, password ]
      rows:
        - [ gaifax, lele, "123456" ]
        - [ foobar, john, "abcdef" ]
        - lastname: rossi
          firstname: paolo
          birthdate: 1950-02-03

If you have a `tab-separated-values`__ file, you may say::

    - entity: model.Cities
      key:
        - name
        - country
      fields: [ name, country ]
      rows: !TSV {path: ../data/cities.txt, encoding: utf-8}

and if the field names are included in the the first row of the file, simply omit the
``fields`` slot::

    - entity: model.Countries
      key:
        - code
      rows: !TSV {path: ../data/countries.txt, encoding: utf-8}

The ``dbloady`` tool iterates over all the entities, and for each instance it determines if it
already exists querying the database with the given *key*: if it's there, it updates it
otherwise it creates a new one and initializes it with its data.

__ https://en.wikipedia.org/wiki/Tab-separated_values


Test fixture facility
---------------------

With the option ``--save-new-instances`` newly created instances will be written (actually
added) to the given file in YAML format, so that at some point they can be deleted using the
option ``--delete`` on that file.  Ideally

::

  dbloady -u postgresql://localhost/test -s new.yaml fixture.yaml
  dbloady -u postgresql://localhost/test -D new.yaml

should remove fixture's traces from the database, if it contains only new data.


Pre and post load scripts
-------------------------

The option ``--preload`` may be used to execute an arbitrary Python script before any load
happens.  This is useful either to tweak the YAML context or to alter the set of file names
specified on the command line (received as the `fnames` global variable).

The following script registers a custom costructor that recognizes the tag ``!time`` or a value
like ``T12:34`` as a ``datetime.time`` value::

  import datetime, re
  from ruamel import yaml

  def time_constructor(loader, node):
      value = loader.construct_scalar(node)
      if value.startswith('T'):
          value = value[1:]
      parts = map(int, value.split(':'))
      return datetime.time(*parts)

  yaml.add_constructor('!time', time_constructor)
  yaml.add_implicit_resolver('!time', re.compile(r'^T?\d{2}:\d{2}(:\d{2})?$'), ['T'])

As another example, the following script handles input files with a ``.gpg`` suffix decrypting
them on the fly to a temporary file that will be deleted when the program exits::

  import atexit, os, subprocess, tempfile

  def decipher(fname):
      print("Input file %s is encrypted, please enter passphrase" % fname)
      with tempfile.NamedTemporaryFile(suffix='.yaml') as f:
          tmpfname = f.name
      subprocess.run(['gpg', '-q', '-o', tmpfname, fname], check=True)
      atexit.register(lambda n=tmpfname: os.unlink(n))
      return tmpfname

  fnames = [decipher(fname) if fname.endswith('.gpg') else fname for fname in fnames]

Then you have::

  dbloady -u postgresql://localhost/test -p preload.py data.yaml.gpg
  Input file data.yaml.gpg is encrypted, please enter passphrase
  /tmp/tmpfhjrdqgf.yaml: ......
  Committing changes

The option ``--postload`` may be used to perform additional steps *after* all YAML files have
been loaded but *before* the DB transaction is committed.

The pre/post load scripts are executed with a context containing the following variables:

`session`
  the SQLAlchemy session

`dry_run`
  the value of the ``--dry-run`` option

`fnames`
  the list of file names specified on the command line


Generic foreign keys
--------------------

Version 1.6 introduced rudimentary and experimental support for the `generic foreign keys`__
trick. It assumes that they are implemented with a `hybrid property`__ that exposes a `custom
comparator`__. See ``tests/generic_fk/model.py`` for an example.

__ http://docs.sqlalchemy.org/en/latest/_modules/examples/generic_associations/generic_fk.html
__ http://docs.sqlalchemy.org/en/rel_1_1/orm/extensions/hybrid.html
__ http://docs.sqlalchemy.org/en/rel_1_1/orm/extensions/hybrid.html#building-custom-comparators

With a proper configuration, the following works::

  - entity: model.Customer
    key: name
    data:
      - &customer
        name: Best customer

  - entity: model.Supplier
    key: company_name
    data:
      - &supplier
        company_name: ACME

  - entity: model.Address
    key:
      - related_object
      - street
    data:
      - related_object: *customer
        street: 123 anywhere street
      - related_object: *supplier
        street: 321 long winding road


Direct assignment of primary keys
---------------------------------

When the attribute does not correspond to a relationship property, assignment of an instance
reference will set the attribute to the instance's primary key::

  - entity: model.Person
    key:
      - lastname
      - firstname
    fields:
      - lastname
      - firstname
    data:
      - &johndoe [ Doe, John ]

  - entity: model.CannedFilter
    key: description
    data:
      - &onlyjohndoe
        description: "Only John Doe"

  - entity: model.Condition
    key:
      - filter
      - fieldname
    data:
      - filter: *onlyjohndoe
        fieldname: "persons.id"
        fieldvalue: *johndoe

Raw SQL values
--------------

Sometime a value requires executing an arbitrary query on the database, maybe because it is
computed by a trigger or more generally because it cannot be determined by the YAML content::

  - entity: model.Number
    key:
      id
    data:
      - id: 1
        absolute: !SQL {query: "SELECT abs(:num)", params: {num: -1}}
      - id: !SQL {query: "SELECT abs(:num)", params: {num: -2}}
        absolute: !SQL {query: "SELECT abs(:num)", params: {num: -2}}
      - id: 3
        absolute: !SQL {query: "SELECT count(*) FROM numbers"}

The specified query must return a single value, as it is executed with `session.scalar()`__.

__ http://docs.sqlalchemy.org/en/latest/orm/session_api.html#sqlalchemy.orm.session.Session.scalar


Data dumper
===========

With the complementary tool, ``dbdumpy``, you can obtain a YAML representation out
of a database in the same format used by ``dbloady``. It's rather simple and in particular it
does not handle reference cycles.

The tool is driven by a `specs file`, a YAML document composed by two parts: the first defines
the `pivots` instances (that is, the entry points), the second describes how each entity must
be serialized and in which order.

Consider the following document::

  - entity: model.Result
  ---
  - entity: model.Person
    key:
      - lastname
      - firstname

  - entity: model.Exam
    fields: description
    key: description

  - entity: model.Result
    key:
      - person
      - exam
    other:
      - vote

It tells ``dbdumpy`` to consider *all* instances of ``model.Result`` as the pivots, then
defines how each entity must be serialized, simply by listing the ``key`` attribute(s) and any
further ``other`` field. Alternatively, you can specify a list of ``fields`` names, to obtain
the more compact form described `above`__.

__ fields_

Executing

::

  dbdumpy -u sqlite:////foo/bar.sqlite spec.yaml

will emit the following on stdout::

  - entity: model.Person
    key:
    - lastname
    - firstname
    rows:
    - &id002
      firstname: John
      lastname: Doe
    - &id003
      firstname: Bar
      lastname: Foo
  - entity: model.Exam
    fields: description
    key: description
    rows:
    - &id001
      - Drive license
  - entity: model.Result
    key:
    - person
    - exam
    rows:
    - exam: *id001
      person: *id002
      vote: 10
    - exam: *id001
      person: *id003
      vote: 5

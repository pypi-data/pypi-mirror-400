# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- M2M test
# :Created:   sab 18 gen 2020, 08:33:00
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2020, 2022 Lele Gaifax
#

import sys

from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


Base = declarative_base()


association_table = Table(
    'association', Base.metadata,
    Column('left_id', Integer, ForeignKey('left.id')),
    Column('right_id', Integer, ForeignKey('right.id'))
)


class Parent(Base):
    __tablename__ = 'left'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    children = relationship("Child", secondary=association_table)


class Child(Base):
    __tablename__ = 'right'
    id = Column(Integer, primary_key=True)
    name = Column(String)


if len(sys.argv) == 3:
    url = f'sqlite:///{sys.argv[2]}'
    e = create_engine(url)

    if sys.argv[1] == 'setup':
        Base.metadata.create_all(e)
    elif sys.argv[1] == 'test':
        smaker = sessionmaker(autoflush=False, autocommit=False, bind=e)
        session = smaker()

        paperino = session.query(Parent).one()
        assert paperino.name == 'Paperino'
        assert len(paperino.children) == 3
        assert paperino.children[0].name == 'Qui'
        assert paperino.children[1].name == 'Quo'
        assert paperino.children[2].name == 'Qua'

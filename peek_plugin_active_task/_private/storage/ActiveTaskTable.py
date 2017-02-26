""" 
 *  Copyright Synerty Pty Ltd 2016
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by 
 *  Synerty Pty Ltd
 *
"""
import logging

from sqlalchemy import Column
from sqlalchemy import Integer, String
from sqlalchemy.sql.schema import Index
from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_active_task._private.PluginNames import activeTaskTuplePrefix
from peek_plugin_active_task._private.storage.DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


@addTupleType
class ActiveTaskTable(Tuple, DeclarativeBase):
    """ ActiveTaskTable

    This table doesn't do anything

    """
    __tupleType__ = activeTaskTuplePrefix + 'ActiveTaskTable'
    __tablename__ = 'ActiveTaskTable'

    id = Column(Integer, primary_key=True, autoincrement=True)
    string1 = Column(String(50))

    nonDbField = TupleField()

    __table_args__ = (
        Index("idx_ActiveTaskTable_unique_index", id, string1,
              unique=True),
    )

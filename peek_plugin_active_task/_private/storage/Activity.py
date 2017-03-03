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
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime
from vortex.Tuple import Tuple, addTupleType

from peek_plugin_active_task._private.PluginNames import activeTaskTuplePrefix
from peek_plugin_active_task._private.storage.DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


@addTupleType
class Activity(Tuple, DeclarativeBase):
    """ Activity

    An Activity represents an item in the activity screen
    This is a screen that is intended to show actions that have been performed recently
        or events that plugins want in this list.
    
    see ActiveTaskAbiABC.NewActivity for documentation.
        
    """
    __tupleType__ = activeTaskTuplePrefix + 'Activity'
    __tablename__ = 'Activity'

    id = Column(Integer, primary_key=True, autoincrement=True)

    uniqueId = Column(String(50), unique=True, nullable=False)
    userId = Column(String(50), nullable=False)
    dateTime = Column(DateTime, nullable=False)

    # The display properties of the task
    title = Column(String(50), nullable=False)
    description = Column(String(200))
    iconPath = Column(String(200))

    # The client_fe_app route to open when this task is selected
    routePath = Column(String(200))
    routeParamJson = Column(String(200))


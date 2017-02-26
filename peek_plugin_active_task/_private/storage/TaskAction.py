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
from sqlalchemy.sql.schema import Index, ForeignKey

from peek_plugin_active_task._private.PluginNames import activeTaskTuplePrefix
from peek_plugin_active_task._private.storage.DeclarativeBase import DeclarativeBase
from vortex.Tuple import Tuple, addTupleType

logger = logging.getLogger(__name__)


@addTupleType
class TaskAction(Tuple, DeclarativeBase):
    """ Task Action

    This table stores the Task Actions.
    Tasks have zero or more actions that can be performed by the user when they
    receive a task.
    
    :member title: The title of the action, this will appear as a menu option.
    :member confirmMessage: This is the message that will be shown to confirm the action.
    :member actionedPayload: This payload will be delivered locally on Peek Server
        When the action is performed on the user device.

    """
    __tupleType__ = activeTaskTuplePrefix + 'TaskAction'
    __tablename__ = 'TaskAction'

    id = Column(Integer, primary_key=True, autoincrement=True)
    taskId = Column(Integer,
                    ForeignKey("Task.id"),
                    nullable=False)

    title = Column(String(50))
    confirmMessage = Column(String(200))
    actionedPayload = Column(String(10000))

    __table_args__ = (
        Index("idx_TaskAction_taskId", taskId, unique=False),
    )

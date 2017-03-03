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
class Task(Tuple, DeclarativeBase):
    """ Task

    A Task represents the feature rich messages that can be sent from initiator 
    plugins to mobile devices.
    
    see ActiveTaskAbiABC.NewTask for documentation.
        
    """
    __tupleType__ = activeTaskTuplePrefix + 'Task'
    __tablename__ = 'Task'

    # Ensure that the actions are serialised
    __fieldNames__ = ["actions"]

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

    # The confirmation options
    confirmedPayload = Column(String(10000))

    '''
    Here we should have 
    * TODO, A task you can mark as done
    * Questions to answer (Yes, No, etc)
    * Active Task (the task you should be working on at present (EG, Issued tasks))
    * Notifications that can be marked as "READ"
    ---
    Rename CONFIRM to READ
    ---
    * Activity history (probably in a separate tab to the tasks)
    ---
    The services need to be global, so fix that (remove zones from vortex)
    '''
    CONFIRM_NONE = 0
    CONFIRM_ON_RECEIPT = 1
    CONFIRM_ON_SELECT = 2
    CONFIRM_ON_ACTION = 3
    confirmType = Column(Integer, nullable=False, server_default='0')

    # The state of this action
    STATE_NEW = 0
    STATE_RECEIVED = 1
    STATE_CONFIRMED = 2
    STATE_ACTIONED = 3
    STATE_ARCHIVED = 4
    state = Column(Integer, nullable=False, server_default='0')

    NOTIFY_BY_DEVICE_POPUP = 1
    NOTIFY_BY_DEVICE_SOUND = 2
    NOTIFY_BY_SMS = 4
    NOTIFY_BY_EMAIL = 8
    notificationType = Column(Integer, nullable=False, server_default='0')
    notificationsSent = Column(Integer, nullable=False, server_default='0')

    # The actions for this Task.
    actions = relationship("TaskAction")

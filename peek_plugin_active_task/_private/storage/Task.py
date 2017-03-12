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

from peek_plugin_active_task._private.PluginNames import activeTaskTuplePrefix
from peek_plugin_active_task._private.storage.DeclarativeBase import DeclarativeBase
from sqlalchemy import Column
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime, LargeBinary
from vortex.Tuple import Tuple, addTupleType

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

    uniqueId = Column(String(100), unique=True, nullable=False)
    userId = Column(String(50), nullable=False)
    dateTime = Column(DateTime, nullable=False)

    # The display properties of the task
    title = Column(String(100), nullable=False)
    description = Column(String(2000))
    iconPath = Column(String(200))

    # The client_fe_app route to open when this task is selected
    routePath = Column(String(200))
    routeParamJson = Column(String(200))

    # The confirmation options
    onDeliveredPayload = Column(LargeBinary)
    onCompletedPayload = Column(LargeBinary)
    onDeletedPayload = Column(LargeBinary)

    AUTO_COMPLETE_OFF = 0
    AUTO_COMPLETE_ON_DELIVER = 1
    AUTO_COMPLETE_ON_SELECT = 2
    AUTO_COMPLETE_ON_ACTION = 4
    autoComplete = Column(Integer, nullable=False, server_default='0')
    autoDeleteDateTime = Column(DateTime, nullable=True)

    AUTO_DELETE_OFF = 0
    AUTO_DELETE_ON_DELIVER = 1
    AUTO_DELETE_ON_SELECT = 2
    AUTO_DELETE_ON_ACTION = 4
    AUTO_DELETE_ON_COMPLETE = 8
    autoDelete = Column(Integer, nullable=False, server_default='0')

    # The state of this action
    STATE_DELIVERED = 1
    STATE_SELECTED = 2
    STATE_ACTIONED = 4
    STATE_COMPLETED = 8
    stateFlags = Column(Integer, nullable=False, server_default='0')

    NOTIFY_BY_DEVICE_POPUP = 1
    NOTIFY_BY_DEVICE_SOUND = 2
    NOTIFY_BY_SMS = 4
    NOTIFY_BY_EMAIL = 8
    notificationRequiredFlags = Column(Integer, nullable=False, server_default='0')
    notificationSentFlags = Column(Integer, nullable=False, server_default='0')

    DISPLAY_AS_TASK = 0
    DISPLAY_AS_MESSAGE = 1
    displayAs = Column(Integer, nullable=False, server_default='0')

    # The actions for this Task.
    actions = relationship("TaskAction")

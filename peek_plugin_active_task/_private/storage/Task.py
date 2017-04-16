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
from peek_plugin_active_task.server.ActiveTaskApiABC import NewTask
from sqlalchemy import Column
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime, LargeBinary
from vortex.Tuple import Tuple, addTupleType

from peek_plugin_base.storage.TypeDecorators import PeekLargeBinary

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

    # The mobile-app route to open when this task is selected
    routePath = Column(String(200))
    routeParamJson = Column(String(200))

    # The confirmation options
    onDeliveredPayload = Column(PeekLargeBinary)
    onCompletedPayload = Column(PeekLargeBinary)
    onDeletedPayload = Column(PeekLargeBinary)

    AUTO_COMPLETE_OFF = NewTask.AUTO_COMPLETE_OFF
    AUTO_COMPLETE_ON_DELIVER = NewTask.AUTO_COMPLETE_ON_DELIVER
    AUTO_COMPLETE_ON_SELECT = NewTask.AUTO_COMPLETE_ON_SELECT
    AUTO_COMPLETE_ON_ACTION = NewTask.AUTO_COMPLETE_ON_ACTION
    autoComplete = Column(Integer, nullable=False, server_default='0')
    autoDeleteDateTime = Column(DateTime, nullable=True)

    AUTO_DELETE_OFF = NewTask.AUTO_DELETE_OFF
    AUTO_DELETE_ON_DELIVER = NewTask.AUTO_DELETE_ON_DELIVER
    AUTO_DELETE_ON_SELECT = NewTask.AUTO_DELETE_ON_SELECT
    AUTO_DELETE_ON_ACTION = NewTask.AUTO_DELETE_ON_ACTION
    AUTO_DELETE_ON_COMPLETE = NewTask.AUTO_DELETE_ON_COMPLETE
    autoDelete = Column(Integer, nullable=False, server_default='0')

    # The state of this action
    STATE_DELIVERED = 1
    STATE_SELECTED = 2
    STATE_ACTIONED = 4
    STATE_COMPLETED = 8
    stateFlags = Column(Integer, nullable=False, server_default='0')

    NOTIFY_BY_DEVICE_POPUP = NewTask.NOTIFY_BY_DEVICE_POPUP
    NOTIFY_BY_DEVICE_SOUND = NewTask.NOTIFY_BY_DEVICE_SOUND
    NOTIFY_BY_SMS = NewTask.NOTIFY_BY_SMS
    NOTIFY_BY_EMAIL = NewTask.NOTIFY_BY_EMAIL
    NOTIFY_BY_DEVICE_DIALOG = NewTask.NOTIFY_BY_DEVICE_DIALOG
    notificationRequiredFlags = Column(Integer, nullable=False, server_default='0')
    notificationSentFlags = Column(Integer, nullable=False, server_default='0')

    DISPLAY_AS_TASK = NewTask.PRIORITY_SUCCESS
    DISPLAY_AS_MESSAGE = NewTask.PRIORITY_SUCCESS
    displayAs = Column(Integer, nullable=False, server_default='0')

    PRIORITY_SUCCESS = NewTask.PRIORITY_SUCCESS
    PRIORITY_INFO = NewTask.PRIORITY_INFO
    PRIORITY_WARNING = NewTask.PRIORITY_WARNING
    PRIORITY_DANGER = NewTask.PRIORITY_DANGER
    displayPriority = Column(Integer, nullable=False, server_default='0')

    # The actions for this Task.
    actions = relationship("TaskAction")

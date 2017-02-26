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
from sqlalchemy.sql.schema import Index
from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_active_task._private.PluginNames import activeTaskTuplePrefix
from peek_plugin_active_task._private.storage.DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


@addTupleType
class Task(Tuple, DeclarativeBase):
    """ Task

    A Task represents the feature rich messages that can be sent from initiator 
    plugins to mobile devices.
    
    :member uniqueId: A unique identifier provided when this task was created.
        The initiating plugin may use this later to cancel the task.
    
    :member title: The title to display in the task.
    :member description: The long text that is displayed under the title for this task.
    :member iconPath: The URL for the icon, if any.

    :member routePath: If this route path is defined, then selecting the task
        will cause the peek client fe to change routes to a new page.
    :member routeParamJson: If the route path is defined, this route param json 
        will be passed along when the route is swtiched.

    :member confirmedPayload: (Optional) The payload that will be delivered locally
        on Peek Server when the message is confirmed.
        
    :member confirmType: The type of confirmation required when the message is
        delivered to the users device.
        
    """
    __tupleType__ = activeTaskTuplePrefix + 'Task'
    __tablename__ = 'Task'

    # Ensure that the actions are serialised
    __fieldNames__ = ["actions"]

    id = Column(Integer, primary_key=True, autoincrement=True)

    uniqueId = Column(String(50), unique=True, nullable=False)

    # The display properties of the task
    title = Column(String(50), nullable=False)
    description = Column(String(200))
    iconPath = Column(String(200))

    # The client_fe route to open when this task is selected
    routePath = Column(String(200))
    routeParamJson = Column(String(200))

    # The confirmation options
    confirmedPayload = Column(String(10000))

    CONFIRM_NONE = 0
    CONFIRM_ON_RECEIPT = 1
    CONFIRM_ON_SELECT = 2
    CONFIRM_ON_ACTION = 3
    confirmType = Column(Integer, nullable=False)

    # The actions for this Task.
    actions = relationship("TaskAction")


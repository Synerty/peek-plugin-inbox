from abc import ABCMeta, abstractmethod
from datetime import datetime

from typing import Optional, List


class NewTask:
    """ TaskTuple

    A TaskTuple represents the feature rich mechanism for notifications, alerts and messages
     sent from initiator plugins to mobile devices.

    :member uniqueId: A unique identifier provided when this task was created.
        The initiating plugin may use this later to cancel the task.
        HINT : Ensure you prefix the uniqueId with your plugin name.

    :member userId: A string representing the unique ID of the user. This must match the
        users plugin.

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

    CONFIRM_NONE = 0
    CONFIRM_ON_RECEIPT = 1
    CONFIRM_ON_SELECT = 2
    CONFIRM_ON_ACTION = 3

    NOTIFY_BY_DEVICE_POPUP = 1
    NOTIFY_BY_DEVICE_SOUND = 2
    NOTIFY_BY_SMS = 4
    NOTIFY_BY_EMAIL = 8

    def __init__(self, uniqueId: str, userId: str, title: str,
                 description: Optional[str] = None, iconPath: Optional[str] = None,
                 routePath: Optional[str] = None, routeParams: Optional[dict] = None,
                 confirmedPayload: Optional[bytes] = None, confirmType: int = 0,
                 notificationType: int = 0,
                 actions: List['NewTaskAction'] = ()):
        self.uniqueId = self._required(uniqueId, "uniqueId")
        self.userId = self._required(userId, "userId")

        # The display properties of the task
        self.title = self._required(title, "title")
        self.description = description
        self.iconPath = iconPath

        # The client_fe_app route to open when this task is selected
        self.routePath = routePath
        self.routeParamJson = routeParams

        # The confirmation options
        self.confirmedPayload = confirmedPayload

        self.confirmType = confirmType

        self.notificationType = notificationType

        # The actions for this TaskTuple.
        self.actions = list(actions)

    def _required(self, val, desc):
        if not val:
            raise Exception("%s is not optional" % desc)

        return val


class NewTaskAction:
    """ TaskTuple Action

    This object represents the TaskTuple Actions.
    Tasks have zero or more actions that can be performed by the user when they
    receive a task.

    :member title: The title of the action, this will appear as a menu option.
    :member confirmMessage: This is the message that will be shown to confirm the action.
    :member actionedPayload: This payload will be delivered locally on Peek Server
        When the action is performed on the user device.

    """

    def __init__(self, title: str, confirmMessage: str,
                 actionedPayload: Optional[bytes] = None):
        self.title = self._required(title, "title")
        self.confirmMessage = self._required(confirmMessage, "confirmMessage")
        self.actionedPayload = self._required(actionedPayload, "actionedPayload")

    def _required(self, val, desc):
        if not val:
            raise Exception("%s is not optional" % desc)

        return val


class NewActivity:
    """ TaskTuple

    A TaskTuple represents the feature rich mechanism for notifications, alerts and messages
     sent from initiator plugins to mobile devices.

    :member uniqueId: A unique identifier provided when this task was created.
        The initiating plugin may use this later to cancel the task.
        HINT : Ensure you prefix the uniqueId with your plugin name.

    :member userId: A string representing the unique ID of the user. This must match the
        users plugin.

    :member title: The title to display in the task.
    :member description: The long text that is displayed under the title for this task.
    :member iconPath: The URL for the icon, if any.

    :member routePath: If this route path is defined, then selecting the task
        will cause the peek client fe to change routes to a new page.
    :member routeParamJson: If the route path is defined, this route param json 
        will be passed along when the route is swtiched.

    """

    def __init__(self, uniqueId: str, userId: str, title: str,
                 dateTime: Optional[datetime] = None,
                 description: Optional[str] = None, iconPath: Optional[str] = None,
                 routePath: Optional[str] = None, routeParams: Optional[dict] = None):
        self.uniqueId = self._required(uniqueId, "uniqueId")
        self.userId = self._required(userId, "userId")
        self.dateTime = dateTime if dateTime else datetime.utcnow()

        # The display properties of the task
        self.title = self._required(title, "title")
        self.description = description
        self.iconPath = iconPath

        # The client_fe_app route to open when this item is selected
        self.routePath = routePath
        self.routeParamJson = routeParams

    def _required(self, val, desc):
        if not val:
            raise Exception("%s is not optional" % desc)

        return val


class ActiveTaskApiABC(metaclass=ABCMeta):
    @abstractmethod
    def addTask(self, task: NewTask) -> None:
        """ Add a New Task

        Add a new task to the users device.
        
        :param task: The definition of the task to add.
        
        """

    @abstractmethod
    def removeTask(self, uniqueId: str) -> None:
        """ Remove a Task
        
        Remove a task from the users device.
        
        :param uniqueId: The uniqueId provided when the task was created.
        """

    @abstractmethod
    def addActivity(self, activity: NewActivity) -> None:
        """ Add a new Activity item

        Add a new Activity to the users device.

        :param activity: The definition of the activity to add.

        """

    @abstractmethod
    def removeActivity(self, uniqueId: str) -> None:
        """ Remove an Activity item

        Remove an Activity from the users device.

        :param uniqueId: The uniqueId provided when the activity was created.
        """

import {activeTaskTuplePrefix} from "../plugin-active-task-names";
import {addTupleType, Tuple} from "@synerty/vortexjs";
import {TaskActionTuple} from "./TaskActionTuple";


@addTupleType
export class TaskTuple extends Tuple {

    static readonly tupleName = activeTaskTuplePrefix + 'Task';

    id: number;

    uniqueId: string;
    userId: string;
    dateTime: Date;

    // The display properties of the task
    title: string;
    description: string;
    iconPath: string;

    // The mobile-app route to open when this task is selected
    routePath: string;
    routeParamJson: {};

    static readonly AUTO_COMPLETE_OFF = 0;
    static readonly AUTO_COMPLETE_ON_DELIVER = 1;
    static readonly AUTO_COMPLETE_ON_SELECT = 2;
    static readonly AUTO_COMPLETE_ON_ACTION = 4;
    autoComplete: number;

    static readonly AUTO_DELETE_OFF = 0;
    static readonly AUTO_DELETE_ON_DELIVER = 1;
    static readonly AUTO_DELETE_ON_SELECT = 2;
    static readonly AUTO_DELETE_ON_ACTION = 4;
    static readonly AUTO_DELETE_ON_COMPLETE = 8;
    autoDelete: number;

    // The state of this action
    static readonly STATE_DELIVERED = 1;
    static readonly STATE_SELECTED = 2;
    static readonly STATE_ACTIONED = 4;
    static readonly STATE_COMPLETED = 8;
    stateFlags: number;

    static readonly NOTIFY_BY_DEVICE_POPUP = 1;
    static readonly NOTIFY_BY_DEVICE_SOUND = 2;
    static readonly NOTIFY_BY_SMS = 4;
    static readonly NOTIFY_BY_EMAIL = 8;
    notificationRequiredFlags: number;
    notificationSentFlags: number;

    static readonly DISPLAY_AS_TASK = 0;
    static readonly DISPLAY_AS_MESSAGE = 1;
    displayAs: number;

    // The actions for this TaskTuple.
    actions: TaskActionTuple[];

    constructor() {
        super(TaskTuple.tupleName);
    }

    // ------------------------------
    // State properties
    isCompleted() {
        return !!(this.stateFlags & TaskTuple.STATE_COMPLETED);
    }

    isActioned() {
        return !!(this.stateFlags & TaskTuple.STATE_ACTIONED);
    }

    isDelivered() {
        return !!(this.stateFlags & TaskTuple.STATE_DELIVERED);
    }

    // ------------------------------
    // Notifications Required properties
    isNotifyBySound() {
        return !!(this.notificationRequiredFlags & TaskTuple.NOTIFY_BY_DEVICE_SOUND);
    }

    isNotifyByPopup() {
        return !!(this.notificationRequiredFlags & TaskTuple.NOTIFY_BY_DEVICE_POPUP);
    }

    // ------------------------------
    // Notifications Sent properties
    isNotifiedBySound() {
        return !!(this.notificationSentFlags & TaskTuple.NOTIFY_BY_DEVICE_SOUND);
    }

    isNotifiedByPopup() {
        return !!(this.notificationSentFlags & TaskTuple.NOTIFY_BY_DEVICE_POPUP);
    }

    // ------------------------------
    // Notification properties
    isTask() {
        return this.displayAs == TaskTuple.DISPLAY_AS_TASK;
    }

    isMessage() {
        return this.displayAs == TaskTuple.DISPLAY_AS_MESSAGE;
    }

}
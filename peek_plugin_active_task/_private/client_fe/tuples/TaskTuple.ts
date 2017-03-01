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

    // The client_fe route to open when this task is selected
    routePath: string;
    routeParamJson: {};


    static readonly CONFIRM_NONE = 0;
    static readonly CONFIRM_ON_RECEIPT = 1;
    static readonly CONFIRM_ON_SELECT = 2;
    static readonly CONFIRM_ON_ACTION = 3;
    confirmType: number;

    // The state of this action
    static readonly STATE_NEW = 0;
    static readonly STATE_RECEIVED = 1;
    static readonly STATE_CONFIRMED = 2;
    static readonly STATE_ACTIONED = 3;
    static readonly STATE_ARCHIVED = 4;
    state: number;

    static readonly NOTIFY_BY_DEVICE_POPUP = 1;
    static readonly NOTIFY_BY_DEVICE_SOUND = 2;
    static readonly NOTIFY_BY_SMS = 4;
    static readonly NOTIFY_BY_EMAIL = 8;
    notificationType: number;
    notificationsSent: number;

    // The actions for this TaskTuple.
    actions: TaskActionTuple[];

    constructor() {
        super(TaskTuple.tupleName);
    }

    // State properties
    isConfirmNone() {
        return this.confirmType === TaskTuple.CONFIRM_NONE;
    }

    isConfirmOnReceipt() {
        return this.confirmType === TaskTuple.CONFIRM_ON_RECEIPT;
    }

    isConfirmOnSelect() {
        return this.confirmType === TaskTuple.CONFIRM_ON_SELECT;
    }

    isConfirmOnAction() {
        return this.confirmType === TaskTuple.CONFIRM_ON_ACTION;
    }

    // State properties
    isStateNew() {
        return this.state === TaskTuple.STATE_NEW;
    }

    isStateReceived() {
        return this.state === TaskTuple.STATE_RECEIVED;
    }

    isStateConfirmed() {
        return this.state === TaskTuple.STATE_CONFIRMED;
    }

    isStateActioned() {
        return this.state === TaskTuple.STATE_ACTIONED;
    }

    isStateActionedOrAbove() {
        return this.state >= TaskTuple.STATE_ACTIONED;
    }

    isStateArchived() {
        return this.state === TaskTuple.STATE_ARCHIVED;
    }

    // State properties
    isNotifyBySound() {
        return this.notificationType & TaskTuple.NOTIFY_BY_DEVICE_SOUND;
    }

    isNotifyByPopup() {
        return this.notificationType & TaskTuple.NOTIFY_BY_DEVICE_POPUP;
    }

}
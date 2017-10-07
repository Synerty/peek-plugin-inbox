import {Injectable} from "@angular/core";
import {
    ComponentLifecycleEventEmitter,
    TupleGenericAction,
    TupleSelector,
    VortexService,
    VortexStatusService,
    TupleActionPushOfflineService,
    TupleDataOfflineObserverService
} from "@synerty/vortexjs";
import {PeekModuleFactory, Sound} from "@synerty/peek-util/index.web";
import {TaskTuple} from "./tuples/TaskTuple";
import {ActivityTuple} from "./tuples/ActivityTuple";
import {Ng2BalloonMsgService, UsrMsgLevel, UsrMsgType} from "@synerty/ng2-balloon-msg";
import {UserService} from "@peek/peek_plugin_user";
import {TitleService} from "@synerty/peek-util";

import {inboxPluginName} from "./plugin-inbox-names";
import {PrivateInboxTupleProviderService} from "./_private/private-inbox-tuple-provider.service";

/**  Root Service
 *
 * This service will be loaded by peek-mobile when the app laods.
 * There will be one instance of it, and it be around for the life of the app.
 *
 * Configure this in plugin_package.json
 */


@Injectable()
export class PluginInboxRootService extends ComponentLifecycleEventEmitter {
    tasks: TaskTuple[] = [];

    private taskSubscription: any | null;
    private activitiesSubscription: any | null;

    private alertSound: Sound;

    constructor(private userService: UserService,
                private userMsgService: Ng2BalloonMsgService,
                private titleService: TitleService,
                vortexService: VortexService,
                vortexStatusService: VortexStatusService,
                private tupleService: PrivateInboxTupleProviderService) {
        super();

        this.alertSound = PeekModuleFactory
            .createSound('/assets/peek_plugin_inbox/alert.mp3');


        let sub = this.userService.loggedInStatus.subscribe(
            (status) => {
                if (status)
                    this.subscribe();
                else
                    this.unsubscribe();
            }
        );

        if (this.userService.loggedIn)
            this.subscribe();

        this.onDestroyEvent.subscribe(() => this.unsubscribe());
    }

    // -------------------------
    // Setup subscriptions when the user changes

    private subscribe() {

        // Load Tasks ------------------

        this.taskSubscription = this.tupleService.tupleDataOfflineObserver
            .subscribeToTupleSelector(this.taskTupleSelector)
            .subscribe((tuples: TaskTuple[]) => {
                this.tasks = tuples;

                let notCompletedCount = 0;
                for (let task of this.tasks) {
                    notCompletedCount += task.isCompleted() ? 0 : 1;
                }

                this.titleService.updateButtonBadgeCount(inboxPluginName,
                    notCompletedCount === 0 ? null : notCompletedCount);

                let updateApplied = this.processNotifications()
                    || this.processDeletesAndCompletes();

                if (updateApplied) {
                    // Update the cached data
                    this.tupleService.tupleDataOfflineObserver.updateOfflineState(
                        this.taskTupleSelector, this.tasks);
                }
            });

        // Load Activities ------------------

        // We don't do anything with the activities, we just want to store
        // them offline.
        this.activitiesSubscription = this.tupleService.tupleDataOfflineObserver
            .subscribeToTupleSelector(this.activityTupleSelector)
            .subscribe((tuples: ActivityTuple[]) => {
            });
    }

    private unsubscribe() {
        if (this.activitiesSubscription != null)
            this.activitiesSubscription.unsubscribe();

        if (this.taskSubscription != null)
            this.taskSubscription.unsubscribe();
    }

    // -------------------------
    // Properties for the UI components to use

    get tupleObserverService(): TupleDataOfflineObserverService {
        return this.tupleService.tupleDataOfflineObserver;
    }

    get tupleActionService(): TupleActionPushOfflineService {
        return this.tupleService.tupleOfflineAction;
    }

    get taskTupleSelector(): TupleSelector {
        return new TupleSelector(TaskTuple.tupleName, {
            userName: this.userService.loggedInUserDetails.userName
        });
    }

    get activityTupleSelector(): TupleSelector {
        return new TupleSelector(ActivityTuple.tupleName, {
            userName: this.userService.loggedInUserDetails.userName
        });
    }


    // -------------------------
    // State update methods from UI
    public taskSelected(taskId: number) {
        this.addTaskStateFlag(taskId, TaskTuple.STATE_SELECTED);
    }

    public taskActioned(taskId: number) {
        this.addTaskStateFlag(taskId, TaskTuple.STATE_ACTIONED);
    }

    private addTaskStateFlag(taskId: number, stateFlag: number) {
        let filtered = this.tasks.filter(t => t.id === taskId);
        if (filtered.length === 0) {
            // This should never happen
            return;
        }

        let thisTask = filtered[0];
        this.sendStateUpdate(thisTask, stateFlag, null);
        this.processDeletesAndCompletes();

        // Update the cached data
        this.tupleService.tupleDataOfflineObserver.updateOfflineState(
            this.taskTupleSelector, this.tasks);
    }

    /** Process Delegates and Complete
     *
     * This method updates the local data only.
     * Server side will apply these updates when it gets state flag updates.
     */
    private processDeletesAndCompletes(): boolean {
        let updateApplied = false;

        let tasksSnapshot = this.tasks.slice();
        for (let task of tasksSnapshot) {

            let autoComplete = task.autoComplete & task.stateFlags;
            let isAlreadyCompleted = TaskTuple.STATE_COMPLETED & task.stateFlags
            if (autoComplete && !isAlreadyCompleted) {
                task.stateFlags = (TaskTuple.STATE_COMPLETED | task.stateFlags);
                updateApplied = true
            }

            // If we're in the state where we should delete, then remove it
            // from our tasks.
            if (task.autoDelete & task.stateFlags) {
                let index = this.tasks.indexOf(task);
                if (index > -1) {
                    this.tasks.splice(index, 1);
                }
                updateApplied = true;
            }
        }

        return updateApplied;
    }

    private processNotifications(): boolean {
        let updateApplied = false;

        for (let task of this.tasks) {
            let notificationSentFlags = 0;
            let newStateMask = 0;

            if (task.isNotifyBySound() && !task.isNotifiedBySound()) {
                this.alertSound.play();
                notificationSentFlags = (
                    notificationSentFlags | TaskTuple.NOTIFY_BY_DEVICE_SOUND);
            }

            if (task.isNotifyByPopup() && !task.isNotifiedByPopup()) {
                this.showMessage(UsrMsgType.Fleeting, task);
                notificationSentFlags = (
                    notificationSentFlags | TaskTuple.NOTIFY_BY_DEVICE_POPUP);
            }

            if (task.isNotifyByDialog() && !task.isNotifiedByDialog()) {
                this.showMessage(UsrMsgType.Confirm, task)
                    .then(() => {
                        this.sendStateUpdate(task,
                            TaskTuple.STATE_DIALOG_CONFIRMED,
                            0
                        );
                    })
                    .catch(err => {
                        let e = `Inbox Dialog Error\n${err}`;
                        console.log(e);
                        this.userMsgService.showError(`Inbox Dialog Error\n${err}`);
                    });

                notificationSentFlags = (
                    notificationSentFlags | TaskTuple.NOTIFY_BY_DEVICE_DIALOG);
            }

            if (!task.isDelivered()) {
                newStateMask = (newStateMask | TaskTuple.STATE_DELIVERED);
            }


            if (notificationSentFlags || newStateMask) {
                updateApplied = true;

                this.sendStateUpdate(task,
                    newStateMask,
                    notificationSentFlags
                );
            }
        }

        return updateApplied;
    }

    private showMessage(type_: UsrMsgType, task: TaskTuple): Promise<null> {
        let level: UsrMsgLevel | null = null;

        switch (task.displayPriority) {
            case TaskTuple.PRIORITY_SUCCESS:
                level = UsrMsgLevel.Success;
                break;

            case TaskTuple.PRIORITY_INFO:
                level = UsrMsgLevel.Info;
                break;

            case TaskTuple.PRIORITY_WARNING:
                level = UsrMsgLevel.Warning;
                break;

            case TaskTuple.PRIORITY_DANGER:
                level = UsrMsgLevel.Error;
                break;

            default:
                throw new Error(`Unknown priority ${task.displayPriority}`);

        }

        let dialogTitle = `New ${task.displayAsText()}`;
        let desc = task.description ? task.description : "";
        let msg = `${task.title}\n\n${desc}`;

        return this.userMsgService.showMessage(
            msg,
            level,
            type_, {
                "confirmText": "Ok",
                "dialogTitle": dialogTitle,
                "routePath": task.routePath

            });
    }


    private sendStateUpdate(task: TaskTuple,
                            stateFlags: number | null,
                            notificationSentFlags: number | null) {
        let action = new TupleGenericAction();
        action.key = TaskTuple.tupleName;
        action.data = {
            id: task.id,
            stateFlags: stateFlags,
            notificationSentFlags: notificationSentFlags
        };
        this.tupleService.tupleOfflineAction.pushAction(action)
            .catch(err => alert(err));


        if (stateFlags != null) {
            task.stateFlags = (task.stateFlags | stateFlags);
        }

        if (notificationSentFlags != null) {
            task.notificationSentFlags =
                (task.notificationSentFlags | notificationSentFlags);
        }
    }


}
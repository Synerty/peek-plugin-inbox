import {Injectable, NgZone} from "@angular/core";
import {
    ComponentLifecycleEventEmitter,
    TupleActionPushNameService,
    TupleActionPushOfflineService,
    TupleDataObservableNameService,
    TupleDataOfflineObserverService,
    TupleGenericAction,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService,
    TupleSelector,
    VortexService,
    VortexStatusService,
    WebSqlFactoryService
} from "@synerty/vortexjs";
import {PeekModuleFactory, Sound} from "@synerty/peek-mobile-util/index.web";
import {TaskTuple} from "./tuples/TaskTuple";
import {ActivityTuple} from "./tuples/ActivityTuple";
import {Ng2BalloonMsgService} from "@synerty/ng2-balloon-msg";
import {UserService} from "@peek/peek_plugin_user";
import {TitleService} from "@synerty/peek-mobile-util";

import {
    activeTaskActionProcessorName,
    activeTaskFilt,
    activeTaskObservableName,
    activeTaskPluginName,
    activeTaskTupleOfflineServiceName
} from "./plugin-active-task-names";

/**  Root Service
 *
 * This service will be loaded by peek-mobile when the app laods.
 * There will be one instance of it, and it be around for the life of the app.
 *
 * Configure this in plugin_package.json
 */


@Injectable()
export class PluginActiveTaskRootService extends ComponentLifecycleEventEmitter {
    private static instanceCount = 0;
    private instanceIndex;
    tasks: TaskTuple[] = [];

    private tupleOfflineAction: TupleActionPushOfflineService;
    private tupleDataOfflineObserver: TupleDataOfflineObserverService;

    private taskSubscription: any | null;
    private activitiesSubscription: any | null;

    private alertSound: Sound;

    constructor(private userService: UserService,
                private userMsgService: Ng2BalloonMsgService,
                private titleService: TitleService,
                vortexService: VortexService,
                vortexStatusService: VortexStatusService,
                webSqlFactory: WebSqlFactoryService,
                zone: NgZone) {
        super();

        this.alertSound = PeekModuleFactory
            .createSound('/assets/peek_plugin_active_task/alert.mp3');


        let tupleDataObservableName = new TupleDataObservableNameService(
            activeTaskObservableName, activeTaskFilt);
        let storageName = new TupleOfflineStorageNameService(
            activeTaskTupleOfflineServiceName);
        let tupleActionName = new TupleActionPushNameService(
            activeTaskActionProcessorName, activeTaskFilt);

        let tupleOfflineStorageService = new TupleOfflineStorageService(
            webSqlFactory, storageName);

        this.tupleDataOfflineObserver = new TupleDataOfflineObserverService(
            vortexService,
            vortexStatusService,
            zone,
            tupleDataObservableName,
            tupleOfflineStorageService);


        this.tupleOfflineAction = new TupleActionPushOfflineService(
            tupleActionName,
            vortexService,
            vortexStatusService,
            webSqlFactory);

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

        // Some singleton debugging
        this.instanceIndex = PluginActiveTaskRootService.instanceCount++;
        console.log("peek-plugin-active-task - PluginActiveTaskRootService LOADED #"
            + this.instanceIndex);

        this.onDestroyEvent.subscribe(() => this.unsubscribe());
    }

    // -------------------------
    // Setup subscriptions when the user changes

    private subscribe() {

        // Load Tasks ------------------

        this.taskSubscription = this.tupleDataOfflineObserver
            .subscribeToTupleSelector(this.taskTupleSelector)
            .subscribe((tuples: TaskTuple[]) => {
                this.tasks = tuples;

                let notCompletedCount = 0;
                for (let task of this.tasks) {
                    notCompletedCount += task.isCompleted() ? 0 : 1;
                }

                this.titleService.updateButtonBadgeCount(activeTaskPluginName,
                    notCompletedCount === 0 ? null : notCompletedCount);

                let updateApplied = this.processNotifications()
                    || this.processDeletesAndCompletes();

                if (updateApplied) {
                    // Update the cached data
                    this.tupleDataOfflineObserver.updateOfflineState(
                        this.taskTupleSelector, this.tasks);
                }
            });

        // Load Activities ------------------

        // We don't do anything with the activities, we just want to store
        // them offline.
        this.activitiesSubscription = this.tupleDataOfflineObserver
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
        return this.tupleDataOfflineObserver;
    }

    get tupleActionService(): TupleActionPushOfflineService {
        return this.tupleOfflineAction;
    }

    get taskTupleSelector(): TupleSelector {
        return new TupleSelector(TaskTuple.tupleName, {
            userId: this.userService.loggedInUserDetails.userId
        });
    }

    get activityTupleSelector(): TupleSelector {
        return new TupleSelector(ActivityTuple.tupleName, {
            userId: this.userService.loggedInUserDetails.userId
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
        this.tupleDataOfflineObserver.updateOfflineState(
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
                let desc = task.description ? task.description : "";
                this.userMsgService.showInfo(`${task.title}\n\n${desc}`);
                notificationSentFlags = (
                notificationSentFlags | TaskTuple.NOTIFY_BY_DEVICE_POPUP);
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
        this.tupleOfflineAction.pushAction(action)
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
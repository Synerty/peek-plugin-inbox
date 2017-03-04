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
import {TaskTuple} from "./tuples/TaskTuple";
import {ActivityTuple} from "./tuples/ActivityTuple";
import {Ng2BalloonMsgService} from "@synerty/ng2-balloon-msg";
import {UserService} from "peek-client/peek_plugin_user";

import {
    activeTaskActionProcessorName,
    activeTaskFilt,
    activeTaskObservableName,
    activeTaskTupleOfflineServiceName
} from "./plugin-active-task-names";

/**  Root Service
 *
 * This service will be loaded by peek-client-fe when the app laods.
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

    constructor(private userService: UserService,
                private userMsgService: Ng2BalloonMsgService,
                vortexService: VortexService,
                vortexStatusService: VortexStatusService,
                webSqlFactory: WebSqlFactoryService,
                zone: NgZone) {
        super();

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
                this.processReceives();
                console.log("PluginActiveTaskRootService Tasks received");
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
    // Logic for the tasks

    private processReceives() {
        for (let task of this.tasks) {
            if (task.isStateNew()) {
                let desc = task.description ? task.description : "";
                let soundDone = task.notificationsSent & TaskTuple.NOTIFY_BY_DEVICE_SOUND;
                let popupDone = task.notificationsSent & TaskTuple.NOTIFY_BY_DEVICE_POPUP;

                let notificationsSentMask = 0;

                if (task.isNotifyBySound() && !soundDone) {
                    let audio = new Audio('/assets/peek_plugin_active_task/alert.mp3');
                    audio.play();
                    notificationsSentMask |= TaskTuple.NOTIFY_BY_DEVICE_SOUND;
                }

                if (task.isNotifyByPopup() && !popupDone) {
                    this.userMsgService.showInfo(`${task.title}\n\n${desc}`);
                    notificationsSentMask |= TaskTuple.NOTIFY_BY_DEVICE_POPUP;
                }

                this.sendStateUpdate(task,
                    TaskTuple.STATE_RECEIVED,
                    notificationsSentMask
                );
            }
        }
    }

    private sendStateUpdate(task: TaskTuple,
                            newState: number | null,
                            notificationsSentMask: number | null) {
        let action = new TupleGenericAction();
        action.key = TaskTuple.tupleName;
        action.data = {
            id: task.id,
            state: newState,
            notificationsSentMask: notificationsSentMask
        };
        this.tupleOfflineAction.pushAction(action)
            .then(() => {
                if (newState != null)
                    task.state = newState;

                if (notificationsSentMask != null)
                    task.notificationsSent |= notificationsSentMask;

                // Update the cached data
                this.tupleDataOfflineObserver.updateOfflineState(
                    this.taskTupleSelector, this.tasks);

            })
            .catch(err => alert(err));
    }


}
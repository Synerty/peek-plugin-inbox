import {PeekComponent} from "@synerty/peek-web-ns";
import {
    ComponentLifecycleEventEmitter,
    TupleActionPushOfflineService,
    TupleDataOfflineObserverService,
    TupleSelector
} from "@synerty/vortexjs";
import {Router} from "@angular/router";
import {TaskTuple} from "./tuples/TaskTuple";
import {Ng2BalloonMsgService} from "@synerty/ng2-balloon-msg";
import {TitleService} from "@synerty/peek-client-fe-util";
import {UserService} from "peek_plugin_user";
import {TupleGenericAction} from "../../../../peek-client-fe/peek_client_fe/node_modules/@synerty/vortexjs/src/vortex/TupleAction";


// MomentJS is declared globally, because the datetime picker needs it
declare var moment: any;

@PeekComponent({
    selector: 'plugin-active-task-admin',
    templateUrl: 'plugin-active-task-client.component.web.html',
    moduleFilename: module.filename
})
export class PluginActiveTaskClientComponent extends ComponentLifecycleEventEmitter {

    tasks: TaskTuple[] = [];

    constructor(private userService: UserService,
                private userMsgService: Ng2BalloonMsgService,
                private tupleDataOfflineObserver: TupleDataOfflineObserverService,
                private tupleOfflineAction: TupleActionPushOfflineService,
                private router: Router,
                titleService: TitleService) {

        super();
        titleService.setTitle("My Tasks");

        // Load Jobs Data ------------------

        let tupleSelector = new TupleSelector(TaskTuple.tupleName, {
            userId: userService.loggedInUserDetails.userId
        });

        let sup = this.tupleDataOfflineObserver.subscribeToTupleSelector(tupleSelector)
            .subscribe((tuples: TaskTuple[]) => {
                this.tasks = tuples.sort(
                    (o1, o2) => o2.dateTime.getTime() - o1.dateTime.getTime()
                );
                this.processReceives();
            });
        this.onDestroyEvent.subscribe(() => sup.unsubscribe());

    }

    // Logic for the tasks

    private processReceives() {
        for (let task of this.tasks) {
            if (task.isStateNew()) {
                let desc = task.description ? task.description : "";
                if (task.isNotifyBySound()) {
                    let audio = new Audio('/assets/peek_plugin_active_task/alert.mp3');
                    audio.play();
                }

                if (task.isNotifyByPopup())
                    alert(`${task.title}\n\n${desc}`);

                this.sendStateUpdate(task, TaskTuple.STATE_RECEIVED);
            }
        }
    }

    private sendStateUpdate(task: TaskTuple, newState: number) {
        let action = new TupleGenericAction();
        action.key = TaskTuple.tupleName;
        action.data = {
            id: task.id,
            state: newState
        };
        this.tupleOfflineAction.pushAction(action)
            .then(() => {
                task.state = newState;
            })
            .catch(err => alert(err));
    }

    // Display methods

    timePast(task:TaskTuple) {
        return moment.duration(new Date().getTime() - task.dateTime.getTime()).humanize();
    }

    // User Actions

    taskClicked(task: TaskTuple) {
        if (task.routePath)
            this.router.navigate([task.routePath]);

        // if (task.isConfirmOnSelect())
        this.sendStateUpdate(task, TaskTuple.STATE_CONFIRMED);
    }

}
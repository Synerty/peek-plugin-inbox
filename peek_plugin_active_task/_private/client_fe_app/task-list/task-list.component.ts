import {PeekComponent} from "@synerty/peek-web-ns";
import {
    ComponentLifecycleEventEmitter,
    TupleActionPushOfflineService,
    TupleGenericAction
} from "@synerty/vortexjs";
import {Router} from "@angular/router";
import {
    PluginActiveTaskRootService,
    TaskActionTuple,
    TaskTuple
} from "peek-client/peek_plugin_active_task";
import {UserService} from "peek-client/peek_plugin_user";


// MomentJS is declared globally, because the datetime picker needs it
declare let moment: any;

@PeekComponent({
    selector: 'plugin-active-task-task-list',
    templateUrl: 'task-list.component.web.html',
    moduleFilename: module.filename
})
export class TaskListComponent extends ComponentLifecycleEventEmitter {

    tasks: TaskTuple[] = [];
    private tupleOfflineAction: TupleActionPushOfflineService;

    constructor(private rootService: PluginActiveTaskRootService,
                private router: Router) {

        super();

        this.tupleOfflineAction = rootService.tupleActionService;

        // Load Tasks ------------------

        let sup = rootService.tupleObserverService
            .subscribeToTupleSelector(rootService.taskTupleSelector)
            .subscribe((tuples: TaskTuple[]) => {
                this.tasks = tuples.sort(
                    (o1, o2) => o2.dateTime.getTime() - o1.dateTime.getTime()
                );
            });
        this.onDestroyEvent.subscribe(() => sup.unsubscribe());

    }

    // Logic for the tasks

    private sendStateUpdate(task: TaskTuple, newState: number | null) {
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

    timePast(task: TaskTuple) {
        return moment.duration(new Date().getTime() - task.dateTime.getTime()).humanize();
    }

    // User Actions

    taskClicked(task: TaskTuple) {
        if (task.routePath)
            this.router.navigate([task.routePath]);

        // if (task.isConfirmOnSelect())
        this.sendStateUpdate(task, TaskTuple.STATE_CONFIRMED);
    }

    actionClicked(task: TaskTuple, taskAction: TaskActionTuple) {
        if (taskAction.confirmMessage) {
            if (!confirm(taskAction.confirmMessage))
                return;
        }

        this.sendStateUpdate(task, TaskTuple.STATE_ACTIONED);

        let action = new TupleGenericAction();
        action.key = TaskActionTuple.tupleName;
        action.data = {id: taskAction.id};
        this.tupleOfflineAction.pushAction(action)
            .catch(err => alert(err));
    }

}
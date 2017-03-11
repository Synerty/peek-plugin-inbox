import {Component} from "@angular/core";
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
} from "@peek-client/peek_plugin_active_task";
import {UserService} from "@peek-client/peek_plugin_user";

import * as moment from "moment";

@Component({
    selector: 'plugin-active-task-task-list',
    templateUrl: 'task-list.component.web.html',
    moduleId: module.id
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


    // Display methods

    hasRoute(task: TaskTuple) {
        return task.routePath != null && task.routePath.length;
    }

    dateTime(task: TaskTuple) {
        return moment(task.dateTime).format('HH:MM DD-MMM');
    }

    timePast(task: TaskTuple) {
        return moment.duration(new Date().getTime() - task.dateTime.getTime()).humanize();
    }

    // User Actions

    taskClicked(task: TaskTuple) {
        if (this.hasRoute(task))
            this.router.navigate([task.routePath]);

        this.rootService.taskSelected(task.id);

    }

    actionClicked(task: TaskTuple, taskAction: TaskActionTuple) {
        if (taskAction.confirmMessage) {
            if (!confirm(taskAction.confirmMessage))
                return;
        }

        let action = new TupleGenericAction();
        action.key = TaskActionTuple.tupleName;
        action.data = {id: taskAction.id};
        this.tupleOfflineAction.pushAction(action)
            .catch(err => alert(err));

        this.rootService.taskActioned(task.id);
    }

}
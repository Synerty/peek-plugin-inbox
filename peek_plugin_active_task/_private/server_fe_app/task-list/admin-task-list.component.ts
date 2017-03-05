import {
    ComponentLifecycleEventEmitter,
    TupleDataObserverService,
    TupleSelector
} from "@synerty/vortexjs";
import {
    TaskTuple
} from "peek-server/peek_plugin_active_task/tuples/TaskTuple";
import {Component} from "@angular/core";


@Component({
    selector: 'admin-active-task-task-list',
    templateUrl: './admin-task-list.component.html'
})
export class AdminTaskListComponent extends ComponentLifecycleEventEmitter {

    tasks: TaskTuple[] = [];
    userId:string = "";

    subscription:any = null;

    constructor(private observerService: TupleDataObserverService) {
        super();

    }

    update() {

        // Load Tasks ------------------

        let tupleSelector = new TupleSelector(TaskTuple.tupleName, {
            userId: this.userId
        });

        if (this.subscription != null)
            this.subscription.unsubscribe();

        this.subscription = this.observerService.subscribeToTupleSelector(tupleSelector)
            .subscribe((tuples: TaskTuple[]) => {
                this.tasks = tuples.sort(
                    (o1, o2) => o2.dateTime.getTime() - o1.dateTime.getTime()
                );
            });
        this.onDestroyEvent.subscribe(() => this.subscription.unsubscribe());

    }

}
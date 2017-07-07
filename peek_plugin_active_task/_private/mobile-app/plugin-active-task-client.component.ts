import {Component} from "@angular/core";
import {ComponentLifecycleEventEmitter} from "@synerty/vortexjs";
import {
    PluginActiveTaskRootService,
    TaskTuple
} from "@peek/peek_plugin_active_task";
import {TitleService} from "@synerty/peek-util";


// MomentJS is declared globally, because the datetime picker needs it
declare let moment: any;

@Component({
    selector: 'plugin-active-task',
    templateUrl: 'plugin-active-task-client.component.web.html',
    moduleId: module.id
})
export class PluginActiveTaskClientComponent extends ComponentLifecycleEventEmitter {

    constructor(rootService: PluginActiveTaskRootService,
                titleService: TitleService) {

        super();
        titleService.setTitle("My Tasks");

        // Load Tasks ------------------

        let sup = rootService.tupleObserverService
            .subscribeToTupleSelector(rootService.taskTupleSelector)
            .subscribe((tuples: TaskTuple[]) => {

            });
        this.onDestroyEvent.subscribe(() => sup.unsubscribe());


    }


}
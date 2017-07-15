import {Component} from "@angular/core";
import {ComponentLifecycleEventEmitter} from "@synerty/vortexjs";
import {
    PluginInboxRootService,
    TaskTuple
} from "@peek/peek_plugin_inbox";
import {TitleService} from "@synerty/peek-util";


// MomentJS is declared globally, because the datetime picker needs it
declare let moment: any;

@Component({
    selector: 'plugin-inbox',
    templateUrl: 'plugin-inbox-client.component.web.html',
    moduleId: module.id
})
export class PluginInboxClientComponent extends ComponentLifecycleEventEmitter {

    constructor(rootService: PluginInboxRootService,
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
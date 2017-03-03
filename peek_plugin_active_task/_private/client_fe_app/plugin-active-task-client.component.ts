import {PeekComponent} from "@synerty/peek-web-ns";
import {
    ComponentLifecycleEventEmitter,
    TupleActionPushOfflineService,
    TupleDataOfflineObserverService,
    TupleSelector,
    TupleGenericAction
} from "@synerty/vortexjs";
import {Router} from "@angular/router";
import {TaskTuple, TaskActionTuple} from "peek-client/peek_plugin_active_task";
import {Ng2BalloonMsgService} from "@synerty/ng2-balloon-msg";
import {TitleService} from "@synerty/peek-client-fe-util";
import {UserService} from "peek-client/peek_plugin_user";


// MomentJS is declared globally, because the datetime picker needs it
declare let moment: any;

@PeekComponent({
    selector: 'plugin-active-task',
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


    }


}
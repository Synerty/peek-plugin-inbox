import {Component} from "@angular/core";
import {ComponentLifecycleEventEmitter} from "@synerty/vortexjs";
import {
    PluginInboxRootService,
    TaskTuple
} from "@peek/peek_plugin_inbox";

import {
    PrivateInboxTupleProviderService
} from "@peek/peek_plugin_inbox/_private/private-inbox-tuple-provider.service";

import {SegmentedBarItem} from "./InboxSegmentedBarDeclaration.web";

// MomentJS is declared globally, because the datetime picker needs it
declare let moment: any;

@Component({
    selector: 'plugin-inbox',
    templateUrl: 'plugin-inbox-client.component.web.html',
    moduleId: module.id
})
export class PluginInboxClientComponent extends ComponentLifecycleEventEmitter {

    barItems  = [new SegmentedBarItem(), new SegmentedBarItem()];
    barIndex = 0;

    constructor(rootService: PluginInboxRootService,
                private tupleService: PrivateInboxTupleProviderService) {
        super();

        this.barItems[0].title = 'Tasks';
        this.barItems[1].title = 'Activity';


    }


}
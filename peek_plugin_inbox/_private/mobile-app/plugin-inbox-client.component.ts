import { Component } from "@angular/core"
import { NgLifeCycleEvents } from "@synerty/peek-plugin-base-js"
import { PluginInboxRootService } from "@peek/peek_plugin_inbox"
import { PrivateInboxTupleProviderService } from "@peek/peek_plugin_inbox/_private/private-inbox-tuple-provider.service"

@Component({
    selector: "plugin-inbox",
    templateUrl: "plugin-inbox-client.component.web.html",
    moduleId: module.id
})
export class PluginInboxClientComponent extends NgLifeCycleEvents {
    barIndex = 0
    
    constructor(
        rootService: PluginInboxRootService,
        private tupleService: PrivateInboxTupleProviderService
    ) {
        super()
    }
}

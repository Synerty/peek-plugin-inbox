import {NgModule, OnDestroy} from "@angular/core";
import {PluginInboxRootService} from "./plugin-inbox-root.service";

/** Client Root Module
 *
 * This module will be loaded by peek-mobile when the app laods.
 * There will be one instance of it, and it be around for the life of the app.
 *
 * Configure this in plugin_package.json
 */

@NgModule({})
export class PluginInboxRootModule implements OnDestroy {
    private static instanceCount = 0;
    private instanceIndex;

    constructor(private inboxRootService: PluginInboxRootService) {
        this.instanceIndex = PluginInboxRootModule.instanceCount++;
        console.log("peek-plugin-inbox - PluginInboxRootModule LOADED #"
            + this.instanceIndex);
    }

    ngOnDestroy() {
        console.log("peek-plugin-inbox - PluginInboxRootModule DESTROYED #"
            + this.instanceIndex);
    }
}
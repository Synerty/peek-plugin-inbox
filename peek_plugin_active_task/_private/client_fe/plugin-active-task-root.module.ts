import {NgModule, OnDestroy} from "@angular/core";
import {PluginActiveTaskClientRootService} from "./plugin-active-task-root.service";

/** Client Root Module
 *
 * This module will be loaded by peek-client-fe when the app laods.
 * There will be one instance of it, and it be around for the life of the app.
 *
 * Configure this in plugin_package.json
 */

@NgModule({})
export class PluginActiveTaskClientRootModule implements OnDestroy {
    private static instanceCount = 0;
    private instanceIndex;

    constructor(private activeTaskRootService: PluginActiveTaskClientRootService) {
        this.instanceIndex = PluginActiveTaskClientRootModule.instanceCount++;
        console.log("peek-plugin-active-task - PluginActiveTaskClientRootModule LOADED #"
            + this.instanceIndex);
    }

    ngOnDestroy() {
        console.log("peek-plugin-active-task - PluginActiveTaskClientRootModule DESTROYED #"
            + this.instanceIndex);
    }
}
import {Injectable, OnDestroy} from "@angular/core";

/**  Root Service
 *
 * This service will be loaded by peek-client-fe when the app laods.
 * There will be one instance of it, and it be around for the life of the app.
 *
 * Configure this in plugin_package.json
 */


@Injectable()
export class PluginActiveTaskRootService implements OnDestroy {
    private static instanceCount = 0;
    private instanceIndex;

    constructor() {
        this.instanceIndex = PluginActiveTaskRootService.instanceCount++;
        console.log("peek-plugin-active-task - PluginActiveTaskRootService LOADED #"
            + this.instanceIndex);
    }

    ngOnDestroy() {
        console.log("peek-plugin-active-task - PluginActiveTaskRootService DESTROYED #"
            + this.instanceIndex);
    }
}
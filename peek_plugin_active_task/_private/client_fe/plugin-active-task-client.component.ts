import {PeekComponent} from "@synerty/peek-web-ns";
import {ComponentLifecycleEventEmitter, VortexService} from "@synerty/vortexjs";
import {activeTaskFilt} from "./plugin-active-task-names";
import {extend} from "@synerty/vortexjs";

@PeekComponent({
    selector: 'plugin-active-task-admin',
    templateUrl: 'plugin-active-task-client.component.web.html',
    moduleFilename: module.filename
})
export class PluginActiveTaskClientComponent extends ComponentLifecycleEventEmitter {

    date: string = "No data yet";
    stopped: boolean = false;

    private filt = extend({
        "key": "sendDate"
    }, activeTaskFilt);

    constructor(vortexService: VortexService) {
        super();

        let loader = vortexService.createTupleLoader(this, this.filt);
        loader.observable
            .subscribe(tuples => {
                // Update our value
                this.date = tuples[0];

            });

        this.onDestroyEvent.subscribe(() => {
            this.stopped = true;
        });

        let loadAgain = () => {
            if (this.stopped)
                return;

            // Schedule a reload in 1 second
            setTimeout(() => {
                loadAgain();
                loader.load()
            }, 2000);
        };

        loadAgain();
    }


}
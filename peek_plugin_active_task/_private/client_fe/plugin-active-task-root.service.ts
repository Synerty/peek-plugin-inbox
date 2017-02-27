import {Injectable, OnDestroy} from "@angular/core";
import {
    Payload,
    Tuple,
    TupleActionABC,
    TupleActionProcessorDelegateABC,
    TupleActionProcessorNameService,
    TupleActionProcessorService,
    VortexService,
    VortexStatusService
} from "@synerty/vortexjs";
import {UserService} from "peek_plugin_user";
import {assert, extend} from "@synerty/vortexjs/src/vortex/UtilMisc";
import {
    activeTaskActionProcessorName,
    activeTaskFilt
} from "./plugin-active-task-names";

/** Client Root Service
 *
 * This service will be loaded by peek-client-fe when the app laods.
 * There will be one instance of it, and it be around for the life of the app.
 *
 * Configure this in plugin_package.json
 */

interface TupleActionCallable {
    (tupleAction: TupleActionABC): Promise<Tuple[]>;
}

class PluginActiveTaskRootSingleton extends TupleActionProcessorDelegateABC {

    private sub: any = null;

    private _delegateCallableByTupleName = {};
    private actionProcessor: TupleActionProcessorService;

    constructor(private vortexService: VortexService,
                private vortexStatusService: VortexStatusService,
                private userService: UserService) {
        super();

        let name = new TupleActionProcessorNameService(
            activeTaskActionProcessorName, activeTaskFilt);
        this.actionProcessor = new TupleActionProcessorService(
            name, vortexService, vortexStatusService);

        this.actionProcessor.setDefaultDelegate(this);

        userService.loggedInStatus
        // .filter(loggedIn => loggedIn === true)
            .subscribe(() => this.updateToken());

        vortexStatusService.isOnline
            .filter(online => online === true)
            .subscribe(() => this.updateToken());

        userService.loggedInStatus
            .filter(loggedIn => loggedIn === false)
            .subscribe(() => {
                if (this.sub != null)
                    this.sub.unsubscribe();
                this.sub = null;
            });

        this.updateToken();
    }


    private updateToken() {
        let updateFilt = extend({
            key: "tokenUpdate",
            peekClientToken: localStorage.getItem('peekClientToken'),
        }, activeTaskFilt);

        let tokenUpdate = new Payload(updateFilt);

        this.vortexService.sendPayload(tokenUpdate);
    }

    /** Add Tuple Action Processor Delegate
     *
     *@param tupleName: The tuple name to process actions for.
     *@param delegate: The delegate to use for processing this tuple name.
     *
     */
    setDelegate(tupleName: string, delegate: TupleActionCallable) {

        assert(!this._delegateCallableByTupleName.hasOwnProperty(tupleName),
            `PluginActiveTaskRootService, `
            + `Tuple name ${tupleName} is already registered`);

        this._delegateCallableByTupleName[tupleName] = delegate;
    }

    processTupleAction(tupleAction: TupleActionABC): Promise<Tuple[]> {

        let tupleName = tupleAction._tupleName();
        let processor = this._delegateCallableByTupleName[tupleName];
        if (processor == null) {
            let msg = `ERROR No delegate registered for ${tupleName}`;
            console.log(msg);
            return new Promise<Tuple[]>((_, reject) => reject(msg));
            // throw new Error(`No delegate registered for ${tupleName}`);
        }

        return processor(tupleAction);
    }
}

@Injectable()
export class PluginActiveTaskRootService implements OnDestroy {
    private static singleton: PluginActiveTaskRootSingleton;
    private singleton: PluginActiveTaskRootSingleton;

    private static instanceCount = 0;
    private instanceIndex;

    constructor(private vortexService: VortexService,
                private vortexStatusService: VortexStatusService,
                private userService: UserService) {

        if (!PluginActiveTaskRootService.singleton) {
            PluginActiveTaskRootService.singleton =
                new PluginActiveTaskRootSingleton(vortexService, vortexStatusService, userService);
        }
        this.singleton = PluginActiveTaskRootService.singleton;

        this.instanceIndex = PluginActiveTaskRootService.instanceCount++;
        console.log("peek-plugin-active-task - PluginActiveTaskRootService LOADED #"
            + this.instanceIndex);
    }

    /** Add Tuple Action Processor Delegate
     *
     *@param tupleName: The tuple name to process actions for.
     *@param delegate: The delegate to use for processing this tuple name.
     *
     */
    setDelegate(tupleName: string, delegate: TupleActionCallable) {
        this.singleton.setDelegate(tupleName, delegate);
    }

    ngOnDestroy() {
        console.log("peek-plugin-active-task - PluginActiveTaskRootService DESTROYED #"
            + this.instanceIndex);
    }

}
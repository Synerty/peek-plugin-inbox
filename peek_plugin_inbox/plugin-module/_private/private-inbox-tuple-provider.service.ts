import {Injectable, NgZone} from "@angular/core";
import {
    TupleActionPushNameService,
    TupleActionPushOfflineService,
    TupleActionPushOfflineSingletonService,
    TupleDataObservableNameService,
    TupleDataOfflineObserverService,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService,
    TupleStorageFactoryService,
    VortexService,
    VortexStatusService
} from "@synerty/vortexjs";
import {UserService} from "@peek/peek_plugin_user";

import {
    inboxActionProcessorName,
    inboxFilt,
    inboxObservableName,
    inboxTupleOfflineServiceName
} from "../plugin-inbox-names";


@Injectable()
export class PrivateInboxTupleProviderService {
    public tupleOfflineAction: TupleActionPushOfflineService;
    public tupleDataOfflineObserver: TupleDataOfflineObserverService;


    constructor(tupleActionSingletonService: TupleActionPushOfflineSingletonService,
                vortexService: VortexService,
                vortexStatusService: VortexStatusService,
                storageFactory: TupleStorageFactoryService,
                zone: NgZone) {


        let tupleDataObservableName = new TupleDataObservableNameService(
            inboxObservableName, inboxFilt);
        let storageName = new TupleOfflineStorageNameService(
            inboxTupleOfflineServiceName);
        let tupleActionName = new TupleActionPushNameService(
            inboxActionProcessorName, inboxFilt);

        let tupleOfflineStorageService = new TupleOfflineStorageService(
            storageFactory, storageName);

        this.tupleDataOfflineObserver = new TupleDataOfflineObserverService(
            vortexService,
            vortexStatusService,
            zone,
            tupleDataObservableName,
            tupleOfflineStorageService);


        this.tupleOfflineAction = new TupleActionPushOfflineService(
            tupleActionName,
            vortexService,
            vortexStatusService,
            tupleActionSingletonService);

    }


}
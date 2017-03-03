import {CommonModule} from "@angular/common";
import {NgModule} from "@angular/core";
import {PluginActiveTaskClientComponent} from "./plugin-active-task-client.component";
import {Routes} from "@angular/router";
import {PeekModuleFactory} from "@synerty/peek-web-ns";
import {
    TupleActionPushNameService,
    TupleActionPushOfflineService,
    TupleActionPushService,
    TupleDataObservableNameService,
    TupleDataObserverService,
    TupleDataOfflineObserverService,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService
} from "@synerty/vortexjs";

import {
    LoggedInGuard,
    LoggedOutGuard,
    ProfileService,
    UserService
} from "peek-client/peek_plugin_user";

import {
    activeTaskActionProcessorName,
    activeTaskFilt,
    activeTaskObservableName,
    activeTaskTupleOfflineServiceName
} from "peek-client/peek_plugin_active_task";
import {ActivityListComponent} from "./activity-list/activity-list.component";
import {TaskListComponent} from "./task-list/task-list.component";


export const pluginRoutes: Routes = [
    {
        path: '',
        component: PluginActiveTaskClientComponent,
        canActivate: [LoggedInGuard]
    },
    {
        path: '**',
        component: PluginActiveTaskClientComponent,
        canActivate: [LoggedInGuard]
    }

];

@NgModule({
    imports: [
        CommonModule,
        PeekModuleFactory.RouterModule.forChild(pluginRoutes)],
    exports: [],
    providers: [
        TupleDataObserverService, TupleDataOfflineObserverService, {
            provide: TupleDataObservableNameService,
            useValue: new TupleDataObservableNameService(
                activeTaskObservableName, activeTaskFilt)
        },
        TupleOfflineStorageService, {
            provide: TupleOfflineStorageNameService,
            useValue: new TupleOfflineStorageNameService(
                activeTaskTupleOfflineServiceName)
        },
        TupleActionPushOfflineService, TupleActionPushService, {
            provide: TupleActionPushNameService,
            useValue: new TupleActionPushNameService(
                activeTaskActionProcessorName, activeTaskFilt)
        },

        // User Providers
        UserService, ProfileService, LoggedInGuard, LoggedOutGuard],
    declarations: [PluginActiveTaskClientComponent,
        TaskListComponent,
        ActivityListComponent
    ]
})
export default class PluginActiveTaskClientModule {
}
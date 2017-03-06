import {CommonModule} from "@angular/common";
import {FormsModule} from "@angular/forms";
import {NgModule} from "@angular/core";
import {PluginActiveTaskAdminComponent} from "./plugin-active-task-admin.component";
import {RouterModule, Routes} from "@angular/router";
import {SendTestTaskComponent} from "./send-test-task/send-test-task.component";
import {SendTestActivityComponent} from "./send-test-activity/send-test-activity.component";
/**
 * Created by peek on 5/12/16.
 *
 */

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

import {activeTaskObservableName,
activeTaskActionProcessorName,
activeTaskFilt,
} from "peek-server/peek_plugin_active_task/plugin-active-task-names";
import {AdminSettingListComponent} from "./setting-list/admin-setting-list.component";
import {AdminTaskListComponent} from "./task-list/admin-task-list.component";
import {AdminActivityListComponent} from "./activity-list/admin-activity-list.component";


export const pluginRoutes: Routes = [
    {
        path: '',
        component: PluginActiveTaskAdminComponent
    }

];

@NgModule({
    imports: [
        CommonModule,
        FormsModule,
        RouterModule.forChild(pluginRoutes)],
    exports: [],
    providers: [
        TupleDataObserverService, {
            provide: TupleDataObservableNameService,
            useValue: new TupleDataObservableNameService(
                activeTaskObservableName, activeTaskFilt)
        }, TupleActionPushService, {
            provide: TupleActionPushNameService,
            useValue: new TupleActionPushNameService(
                activeTaskActionProcessorName, activeTaskFilt)
        }
        ],
    declarations: [PluginActiveTaskAdminComponent,
        SendTestTaskComponent,
        SendTestActivityComponent,
        AdminSettingListComponent,
        AdminTaskListComponent,
        AdminActivityListComponent
    ]
})
export default class PluginActiveTaskAdminModule {

}
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
    providers: [],
    declarations: [PluginActiveTaskAdminComponent,
        SendTestTaskComponent,
        SendTestActivityComponent]
})
export default class PluginActiveTaskAdminModule {

}
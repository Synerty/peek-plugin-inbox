import {CommonModule} from "@angular/common";
import {NgModule} from "@angular/core";
import {PluginActiveTaskAdminComponent} from "./plugin-active-task-admin.component";
import {Routes, RouterModule} from "@angular/router";
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
        RouterModule.forChild(pluginRoutes)],
    exports: [],
    providers: [],
    declarations: [PluginActiveTaskAdminComponent]
})
export default class PluginActiveTaskAdminModule {

}
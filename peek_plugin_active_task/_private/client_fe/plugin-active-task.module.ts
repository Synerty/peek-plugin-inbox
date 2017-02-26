import {CommonModule} from "@angular/common";
import {NgModule} from "@angular/core";
import {PluginActiveTaskClientComponent} from "./plugin-active-task-client.component";
import {Routes, RouterModule} from "@angular/router";
import {PeekModuleFactory} from "@synerty/peek-web-ns";
// import {PeekPluginMenuI, PeekPluginMenuItem} from "interfaces/PeekPluginMenuItem";
/**
 * Created by peek on 5/12/16.
 */


export const pluginRoutes: Routes = [
    {
        path: '',
        component: PluginActiveTaskClientComponent,
        data : {title:"activeTask home route"}
    },
    {
        path: '**',
        component: PluginActiveTaskClientComponent,
        data : {title:"activeTask catch all route"}
    }

];

@NgModule({
    imports: [
        CommonModule,
        PeekModuleFactory.RouterModule.forChild(pluginRoutes)],
    exports: [],
    providers: [],
    declarations: [PluginActiveTaskClientComponent]
})
export default class PluginActiveTaskClientModule
// implements PeekPluginMenuI
{
    // menuRoot(): PeekPluginMenuItem
    // {
    //     return {
    //         name: "ActiveTask",
    //         url: "subItems",
    //         subItems: []
    //     }
    // }
}
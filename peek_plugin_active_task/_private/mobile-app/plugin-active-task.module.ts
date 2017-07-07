import {CommonModule} from "@angular/common";
import {NgModule} from "@angular/core";
import {PluginActiveTaskClientComponent} from "./plugin-active-task-client.component";
import {Routes} from "@angular/router";
import {PeekModuleFactory} from "@synerty/peek-util/index.web";

import {
    LoggedInGuard,
    LoggedOutGuard,
    ProfileService,
    UserService
} from "@peek/peek_plugin_user";

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
        PeekModuleFactory.RouterModule.forChild(pluginRoutes),
        ...PeekModuleFactory.FormsModules
    ],
    exports: [],
    providers: [
        // User Providers
        UserService, ProfileService, LoggedInGuard, LoggedOutGuard],
    declarations: [PluginActiveTaskClientComponent,
        TaskListComponent,
        ActivityListComponent
    ]
})
export class PluginActiveTaskClientModule {
}
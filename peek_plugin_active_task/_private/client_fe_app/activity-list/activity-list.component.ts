import {Component} from "@angular/core";
import {
    ComponentLifecycleEventEmitter,
    TupleActionPushOfflineService,
    TupleDataOfflineObserverService,
    TupleSelector
} from "@synerty/vortexjs";
import {Router} from "@angular/router";
import {
    ActivityTuple,
    PluginActiveTaskRootService
} from "@peek-client/peek_plugin_active_task";
import {UserService} from "@peek-client/peek_plugin_user";


// MomentJS is declared globally, because the datetime picker needs it
declare let moment: any;

@Component({
    selector: 'plugin-active-task-activity-list',
    templateUrl: 'activity-list.component.web.html',
    moduleId: module.id
})
export class ActivityListComponent extends ComponentLifecycleEventEmitter {

    activities: ActivityTuple[] = [];

    private tupleDataOfflineObserver: TupleDataOfflineObserverService;
    private tupleOfflineAction: TupleActionPushOfflineService;

    constructor(private rootService: PluginActiveTaskRootService,
                private router: Router) {

        super();

        this.tupleDataOfflineObserver = rootService.tupleObserverService;
        this.tupleOfflineAction = rootService.tupleActionService;

        // Load Activities ------------------

        let sup = this.tupleDataOfflineObserver
            .subscribeToTupleSelector(rootService.activityTupleSelector)
            .subscribe((tuples: ActivityTuple[]) => {
                this.activities = tuples.sort(
                    (o1, o2) => o2.dateTime.getTime() - o1.dateTime.getTime()
                );
            });
        this.onDestroyEvent.subscribe(() => sup.unsubscribe());

    }


    // Display methods

    hasRoute(activity: ActivityTuple) {
        return activity.routePath != null && activity.routePath.length;
    }

    dateTime(activity: ActivityTuple) {
        return moment(activity.dateTime).format('HH:MM DD-MMM');
    }

    timePast(activity: ActivityTuple) {
        return moment.duration(new Date().getTime() - activity.dateTime.getTime()).humanize();
    }

    // User Actions

    activityClicked(activity: ActivityTuple) {
        if (this.hasRoute(activity))
            this.router.navigate([activity.routePath]);

    }


}
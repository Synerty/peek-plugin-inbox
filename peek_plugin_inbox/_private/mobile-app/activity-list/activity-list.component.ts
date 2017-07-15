import {Component} from "@angular/core";
import {
    ComponentLifecycleEventEmitter,
    TupleActionPushOfflineService,
    TupleDataOfflineObserverService
} from "@synerty/vortexjs";
import {Router} from "@angular/router";
import {
    ActivityTuple,
    PluginInboxRootService
} from "@peek/peek_plugin_inbox";


import * as moment from "moment";

@Component({
    selector: 'plugin-inbox-activity-list',
    templateUrl: 'activity-list.component.web.html',
    moduleId: module.id
})
export class ActivityListComponent extends ComponentLifecycleEventEmitter {

    activities: ActivityTuple[] = [];

    private tupleDataOfflineObserver: TupleDataOfflineObserverService;
    private tupleOfflineAction: TupleActionPushOfflineService;

    constructor(private rootService: PluginInboxRootService,
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

    nsTimeStr(activity) {
        return `${this.dateTime(activity)}, ${this.timePast(activity)} ago`;
    }

    // User Actions

    activityClicked(activity: ActivityTuple) {
        if (this.hasRoute(activity))
            this.router.navigate([activity.routePath]);

    }


}
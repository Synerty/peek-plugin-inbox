import {PeekComponent} from "@synerty/peek-web-ns";
import {
    ComponentLifecycleEventEmitter,
    TupleActionPushOfflineService,
    TupleDataOfflineObserverService,
    TupleSelector,
    TupleGenericAction
} from "@synerty/vortexjs";
import {Router} from "@angular/router";
import {ActivityTuple} from "../tuples/ActivityTuple";
import {Ng2BalloonMsgService} from "@synerty/ng2-balloon-msg";
import {UserService} from "peek_plugin_user";


// MomentJS is declared globally, because the datetime picker needs it
declare let moment: any;

@PeekComponent({
    selector: 'plugin-active-task-activity-list',
    templateUrl: 'activity-list.component.web.html',
    moduleFilename: module.filename
})
export class ActivityListComponent extends ComponentLifecycleEventEmitter {

    activities: ActivityTuple[] = [];

    constructor(private userService: UserService,
                private userMsgService: Ng2BalloonMsgService,
                private tupleDataOfflineObserver: TupleDataOfflineObserverService,
                private tupleOfflineAction: TupleActionPushOfflineService,
                private router: Router) {

        super();
        
        // Load Activities ------------------

        let tupleSelector = new TupleSelector(ActivityTuple.tupleName, {
            userId: userService.loggedInUserDetails.userId
        });

        let sup = this.tupleDataOfflineObserver.subscribeToTupleSelector(tupleSelector)
            .subscribe((tuples: ActivityTuple[]) => {
                this.activities = tuples.sort(
                    (o1, o2) => o2.dateTime.getTime() - o1.dateTime.getTime()
                );
            });
        this.onDestroyEvent.subscribe(() => sup.unsubscribe());

    }


    // Display methods

    timePast(activity: ActivityTuple) {
        return moment.duration(new Date().getTime() - activity.dateTime.getTime()).humanize();
    }

    // User Actions

    activityClicked(activity: ActivityTuple) {
        if (activity.routePath)
            this.router.navigate([activity.routePath]);

    }


}
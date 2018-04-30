import {Component} from "@angular/core";
import {
    extend,
    ComponentLifecycleEventEmitter,
    Payload,
    TupleActionPushService,
    VortexService
} from "@synerty/vortexjs";
import {Ng2BalloonMsgService} from "@synerty/ng2-balloon-msg";


// MomentJS is declared globally, because the datetime picker needs it
// declare let moment: any;

import * as moment from "moment";
import {AdminSendTestActivityActionTuple} from "@peek/peek_plugin_inbox/_private/tuples";

@Component({
    selector: 'active-task-send-test-activity',
    templateUrl: 'send-test-activity.component.html',
    styleUrls: ['send-test-activity.component.css']
})
export class SendTestActivityComponent extends ComponentLifecycleEventEmitter {
    activity = {
        autoDeleteDateTime: moment().add(1, 'days').format('YYYY-MM-DDTHH:mm')
    };

    constructor(private tupleActionPush: TupleActionPushService,
                private balloonMsg: Ng2BalloonMsgService) {
        super();

    }

    send() {
        let activityCopy = extend({}, this.activity);
        activityCopy.autoDeleteDateTime = moment(activityCopy.autoDeleteDateTime).toDate();

        let action = new AdminSendTestActivityActionTuple();
        action.formData = activityCopy;
        this.tupleActionPush.pushAction(action)
            .then(() => this.balloonMsg.showSuccess("Activity created successfully"))
            .catch(e => this.balloonMsg.showError(`Failed to create activity ${e}`));
    }
}

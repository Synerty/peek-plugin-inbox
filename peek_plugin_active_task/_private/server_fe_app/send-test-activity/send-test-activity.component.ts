import {Component} from "@angular/core";
import {ComponentLifecycleEventEmitter, Payload, VortexService} from "@synerty/vortexjs";
import {Ng2BalloonMsgService} from "@synerty/ng2-balloon-msg";


// MomentJS is declared globally, because the datetime picker needs it
declare let moment: any;

@Component({
    selector: 'active-task-send-test-activity',
    templateUrl: 'send-test-activity.component.html',
    styleUrls: ['send-test-activity.component.css']
})
export class SendTestActivityComponent extends ComponentLifecycleEventEmitter {
    activity = {
        autoDeleteDateTime: moment(new Date()).add(1, 'D').toDate()
    };

    private readonly filt = {
        "plugin": "peek_plugin_active_task",
        "key": "sendTestActivity"
    };

    constructor(private vortexService: VortexService, private balloonMsg: Ng2BalloonMsgService) {
        super();

        vortexService.createEndpointObservable(this, this.filt)
            .subscribe(payload => {
                if (payload.result == null || payload.result === true) {
                    balloonMsg.showSuccess("Test Activity Sent Successfully");
                } else {
                    balloonMsg.showError("Test Activity Failed : " + payload.result);
                }
            });


    }

    send() {
        this.vortexService.sendPayload(new Payload(this.filt, [this.activity]));
    }
}

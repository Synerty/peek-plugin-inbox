import {Component} from "@angular/core";
import {ComponentLifecycleEventEmitter, Payload, VortexService} from "@synerty/vortexjs";
import {Ng2BalloonMsgService} from "@synerty/ng2-balloon-msg";


@Component({
    selector: 'active-task-send-test-task',
    templateUrl: 'send-test-task.component.html',
    styleUrls: ['send-test-task.component.css']
})
export class SendTestTaskComponent extends ComponentLifecycleEventEmitter {
    task = {
        actions: [{}]
    };

    private readonly filt = {
        "plugin": "peek_plugin_active_task",
        "key": "sendTestTask"
    };

    constructor(private vortexService: VortexService, private balloonMsg: Ng2BalloonMsgService) {
        super();

        vortexService.createEndpointObservable(this, this.filt)
            .subscribe(payload => {
                if (payload.result == null || payload.result === true) {
                    balloonMsg.showSuccess("Test Task Sent Successfully");
                } else {
                    balloonMsg.showError("Test Task Failed : " + payload.result);
                }
            });


    }

    send() {
        this.vortexService.sendPayload(new Payload(this.filt, [this.task]));
    }
}

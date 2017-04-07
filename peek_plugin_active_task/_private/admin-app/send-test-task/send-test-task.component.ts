import {Component} from "@angular/core";
import {ComponentLifecycleEventEmitter, Payload, VortexService, extend} from "@synerty/vortexjs";
import {Ng2BalloonMsgService} from "@synerty/ng2-balloon-msg";


import * as moment from "moment";

@Component({
    selector: 'active-task-send-test-task',
    templateUrl: 'send-test-task.component.html',
    styleUrls: ['send-test-task.component.css']
})
export class SendTestTaskComponent extends ComponentLifecycleEventEmitter {
    task = {
        notificationRequiredFlags: 0,
        notifyByPopup:false,
        notifyBySound:false,
        notifyBySms:false,
        notifyByEmail:false,
        displayAs:0,
        autoComplete:0,
        autoDelete:0,
        actions: [],
        autoDeleteDateTime: moment().add(1, 'days').format('YYYY-MM-DDTHH:mm')
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

    addAction() {
        this.task.actions.push({});
    }

    send() {
        this.task.notificationRequiredFlags = 0;
        if (this.task.notifyByPopup)
            this.task.notificationRequiredFlags += 1;
        if (this.task.notifyBySound)
            this.task.notificationRequiredFlags += 2;
        if (this.task.notifyBySms)
            this.task.notificationRequiredFlags += 4;
        if (this.task.notifyByEmail)
            this.task.notificationRequiredFlags += 8;

        let taskCopy = extend({},this.task);
        delete taskCopy.notifyByPopup;
        delete taskCopy.notifyBySound;
        delete taskCopy.notifyBySms;
        delete taskCopy.notifyByEmail;
        taskCopy.autoDeleteDateTime = moment(taskCopy.autoDeleteDateTime).toDate();


        this.vortexService.sendPayload(new Payload(this.filt, [taskCopy]));
    }
}

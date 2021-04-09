import { Injectable } from "@angular/core"
import { NgLifeCycleEvents, TupleGenericAction } from "@synerty/vortexjs"
import {
    BalloonMsgLevel,
    BalloonMsgService,
    BalloonMsgType,
    HeaderService,
    ISound,
    Sound,
} from "@synerty/peek-plugin-base-js"
import { TaskTuple } from "../tuples/TaskTuple"
import { inboxPluginName } from "../plugin-inbox-names"
import { PrivateInboxTupleProviderService } from "./private-inbox-tuple-provider.service"
import { PermissionType, Plugins } from "@capacitor/core"
import { DeviceEnrolmentService } from "@peek/peek_core_device"
import { first } from "rxjs/operators"

const {LocalNotifications, Permissions, Modals} = Plugins

/**  Root Service
 *
 * This service will be loaded by peek-field-app when the app loads.
 * There will be one instance of it, and it be around for the life of the app.
 *
 * Configure this in plugin_package.json
 */
@Injectable()
export class PluginInboxRootService extends NgLifeCycleEvents {
    private tasks: TaskTuple[] = []
    private alertSound: ISound
    
    constructor(
        private balloonMsg: BalloonMsgService,
        private headerService: HeaderService,
        private tupleService: PrivateInboxTupleProviderService,
        private deviceService: DeviceEnrolmentService,
    ) {
        super()
        
        try {
            this.alertSound = new Sound("/assets/peek_plugin_inbox/alert.mp3")
        }
        catch (e) {
            console.log(`Failed to load sound: ${e}`)
            this.alertSound = null
        }
        
        // Check notification permissions when deviceInfo is available
        this.deviceService.deviceInfoObservable()
            .pipe(first())
            .subscribe((deviceInfo) => {
                if (!this.deviceService.deviceInfo.isWeb) {
                    this.checkNotificationSettings()
                }
            })
        
        // Subscribe to the tuple events.
        this.tupleService.taskTupleObservable()
            .takeUntil(this.onDestroyEvent)
            .subscribe((tuples: TaskTuple[]) => {
                // Make sure we have the latest flags, to avoid notifying the user again.
                const existingTasksById = {}
                
                for (const task of this.tasks) {
                    existingTasksById[task.id] = task
                }
                
                for (let task of tuples) {
                    const existingTask = existingTasksById[task.id]
                    if (existingTask == null)
                        continue
                    
                    task.stateFlags = (task.stateFlags | existingTask.stateFlags)
                    
                    task.notificationSentFlags = (
                        task.notificationSentFlags | existingTask.notificationSentFlags
                    )
                }
                
                // Now we can set the tasks
                this.tasks = tuples
                
                let notCompletedCount = 0
                for (let task of this.tasks) {
                    notCompletedCount += task.isCompleted() ? 0 : 1
                }
                
                this.headerService.updateBadgeCount(inboxPluginName, notCompletedCount)
                
                const updateApplied = this.processNotifications()
                    || this.processDeletesAndCompletes()
                
                if (updateApplied) {
                    // Update the cached data
                    this.tupleService.tupleDataOfflineObserver.updateOfflineState(
                        this.tupleService.taskTupleSelector,
                        this.tasks
                    )
                }
            })
    }
    
    public taskSelected(taskId: number) {
        this.addTaskStateFlag(taskId, TaskTuple.STATE_SELECTED)
    }
    
    public taskActioned(taskId: number) {
        this.addTaskStateFlag(taskId, TaskTuple.STATE_ACTIONED)
    }
    
    private async checkNotificationSettings(): Promise<void> {
        const permission = await Permissions.query({name: PermissionType.Notifications})
        
        if (permission.state === "prompt") {
            LocalNotifications.requestPermission()
            return
        }
        if (permission.state === "denied") {
            const confirmed = await Modals.confirm({
                title: "Notifications Required",
                message: "Peek requires notifications to be enabled.\n"
                    + "Would you like to enable them now?"
            })
            
            // Open notification settings
            if (confirmed) {
                (window as any)?.cordova?.plugins?.settings?.open(
                    "notification_id",
                    () => console.log("Opened settings."),
                    () => console.log("Failed to open settings.")
                )
            }
            return
        }
    }
    
    private addTaskStateFlag(
        taskId: number,
        stateFlag: number
    ) {
        const filtered = this.tasks.filter(t => t.id === taskId)
        if (filtered.length === 0) {
            // This should never happen
            return
        }
        
        const thisTask = filtered[0]
        this.sendStateUpdate(thisTask, stateFlag, null)
        this.processDeletesAndCompletes()
        
        // Update the cached data
        this.tupleService.tupleDataOfflineObserver.updateOfflineState(
            this.tupleService.taskTupleSelector,
            this.tasks
        )
    }
    
    /** Process Delegates and Complete
     *
     * This method updates the local data only.
     * Server side will apply these updates when it gets state flag updates.
     */
    private processDeletesAndCompletes(): boolean {
        let updateApplied = false
        
        const tasksSnapshot = this.tasks.slice()
        for (let task of tasksSnapshot) {
            
            const autoComplete = task.autoComplete & task.stateFlags
            const isAlreadyCompleted = TaskTuple.STATE_COMPLETED & task.stateFlags
            if (autoComplete && !isAlreadyCompleted) {
                task.stateFlags = (TaskTuple.STATE_COMPLETED | task.stateFlags)
                updateApplied = true
            }
            
            // If we're in the state where we should delete, then remove it
            // from our tasks.
            if (task.autoDelete & task.stateFlags) {
                const index = this.tasks.indexOf(task)
                if (index > -1) {
                    this.tasks.splice(index, 1)
                }
                updateApplied = true
            }
        }
        
        return updateApplied
    }
    
    private processNotifications(): boolean {
        let updateApplied = false
        
        for (const task of this.tasks) {
            let notificationSentFlags = 0
            let newStateMask = 0
            
            if (task.isNotifyBySound() && !task.isNotifiedBySound()) {
                
                notificationSentFlags = (
                    notificationSentFlags | TaskTuple.NOTIFY_BY_DEVICE_SOUND
                )
                
                try {
                    const optionalPromise = this.alertSound && this.alertSound.play()
                    if (optionalPromise != null) {
                        optionalPromise
                            .catch(err => {
                                console.log(`Failed to play alert sound\n${err}`)
                            })
                    }
                }
                catch (e) {
                    console.log(`Error playing sound: ${e.toString()}`)
                }
            }
            
            if (task.isNotifyByPopup() && !task.isNotifiedByPopup()) {
                this.showMessage(BalloonMsgType.Fleeting, task)
                notificationSentFlags = (
                    notificationSentFlags | TaskTuple.NOTIFY_BY_DEVICE_POPUP
                )
            }
            
            if (task.isNotifyByDialog() && !task.isNotifiedByDialog()) {
                this.showMessage(BalloonMsgType.Confirm, task)
                    .then(() => {
                        this.sendStateUpdate(task,
                            TaskTuple.STATE_DIALOG_CONFIRMED,
                            0
                        )
                    })
                    .catch(err => {
                        const e = `Inbox Dialog Error\n${err}`
                        console.log(e)
                        this.balloonMsg.showError(e)
                    })
                
                notificationSentFlags = (
                    notificationSentFlags | TaskTuple.NOTIFY_BY_DEVICE_DIALOG)
            }
            
            if (!task.isDelivered()) {
                newStateMask = (newStateMask | TaskTuple.STATE_DELIVERED)
            }
            
            if (notificationSentFlags || newStateMask) {
                updateApplied = true
                
                this.sendStateUpdate(
                    task,
                    newStateMask,
                    notificationSentFlags
                )
            }
        }
        
        return updateApplied
    }
    
    private showMessage(
        type_: BalloonMsgType,
        task: TaskTuple
    ): Promise<null> {
        let level: BalloonMsgLevel | null = null
        
        switch (task.displayPriority) {
            case TaskTuple.PRIORITY_SUCCESS:
                level = BalloonMsgLevel.Success
                break
            
            case TaskTuple.PRIORITY_INFO:
                level = BalloonMsgLevel.Info
                break
            
            case TaskTuple.PRIORITY_WARNING:
                level = BalloonMsgLevel.Warning
                break
            
            case TaskTuple.PRIORITY_DANGER:
                level = BalloonMsgLevel.Error
                break
            
            default:
                throw new Error(`Unknown priority ${task.displayPriority}`)
        }
        
        const dialogTitle = `New ${task.displayAsText()}`
        const desc = task.description ? task.description : ""
        const msg = `${task.title}\n\n${desc}`
        
        // Send local notification
        if (
            !this.deviceService.deviceInfo.isWeb
            && this.deviceService.deviceInfo.isBackgrounded
        ) {
            this.sendLocalNotification(dialogTitle, desc, 5)
        }
        
        return this.balloonMsg.showMessage(
            msg,
            level,
            type_,
            {
                confirmText: "Ok",
                dialogTitle,
                routePath: task.routePath
            })
    }
    
    private sendLocalNotification(
        title: string,
        body: string,
        seconds: number
    ): void {
        LocalNotifications.schedule({
            notifications: [
                {
                    title,
                    body,
                    id: new Date().getTime(),
                    schedule: {at: new Date(Date.now() + 1000 * seconds)},
                    sound: null,
                    attachments: null,
                    actionTypeId: "",
                    extra: null
                }
            ]
        })
    }
    
    private sendStateUpdate(
        task: TaskTuple,
        stateFlags: number | null,
        notificationSentFlags: number | null
    ) {
        const action = new TupleGenericAction()
        action.key = TaskTuple.tupleName
        action.data = {
            id: task.id,
            stateFlags: stateFlags,
            notificationSentFlags: notificationSentFlags
        }
        this.tupleService.tupleOfflineAction.pushAction(action)
            .catch(err => alert(err))
        
        if (stateFlags != null) {
            task.stateFlags = (task.stateFlags | stateFlags)
        }
        
        if (notificationSentFlags != null) {
            task.notificationSentFlags = (
                task.notificationSentFlags | notificationSentFlags
            )
        }
    }
}

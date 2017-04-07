import {activeTaskTuplePrefix} from "../plugin-active-task-names";
import {addTupleType, Tuple} from "@synerty/vortexjs";


@addTupleType
export class ActivityTuple extends Tuple {

    static readonly tupleName = activeTaskTuplePrefix + 'Activity';

    id: number;

    uniqueId: string;
    userId: string;
    dateTime: Date;

    // The display properties of the task
    title: string;
    description: string;
    iconPath: string;

    // The mobile-app route to open when this task is selected
    routePath: string;
    routeParamJson: {};


    constructor() {
        super(ActivityTuple.tupleName);
    }


}
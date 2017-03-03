

import {activeTaskTuplePrefix} from "../plugin-active-task-names";
import {Tuple, addTupleType} from "@synerty/vortexjs";

@addTupleType
export class TaskActionTuple extends Tuple {

    static readonly tupleName =  activeTaskTuplePrefix + 'TaskAction';

    id :number;
    taskId :number;
    title :string;
    confirmMessage :string;

    constructor() {
        super(TaskActionTuple.tupleName);
    }
}
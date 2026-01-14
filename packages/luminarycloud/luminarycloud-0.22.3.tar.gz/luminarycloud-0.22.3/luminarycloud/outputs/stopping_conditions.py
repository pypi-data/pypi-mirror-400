# Copyright 2025 Luminary Cloud, Inc. All Rights Reserved.

from .._client import get_default_client
from .._proto.api.v0.luminarycloud.stopping_condition import stopping_condition_pb2 as stopcondpb
from .._proto.api.v0.luminarycloud.simulation import simulation_pb2 as simulationpb
from .._proto.output import output_pb2 as outputpb
from dataclasses import dataclass


@dataclass
class StoppingCondition:
    id: str
    "Unique ID"
    output_definition_id: str
    "ID of the output definition defining the quantity to monitor."
    threshold: float
    "The threshold beyond which the condition is met."
    start_at_iteration: int
    "The starting iteration for this condition. The condition will evaluate to false before this iteration is reached."
    averaging_iterations: int
    "Trailing average window length. Number of iterations over which the monitored value is averaged before the tolerance check is applied."
    iterations_to_consider: int
    "Number of (averaged) iterations to consider when determining maximum percent deviation from the current value."

    @classmethod
    def _from_proto(cls, proto: stopcondpb.StoppingCondition) -> "StoppingCondition":
        return cls(
            id=proto.id,
            output_definition_id=proto.output_definition_id,
            threshold=proto.threshold,
            start_at_iteration=proto.start_at_iteration,
            averaging_iterations=proto.averaging_iterations,
            iterations_to_consider=proto.iterations_to_consider,
        )


@dataclass
class GeneralStoppingConditions:
    max_iterations: int
    "Maximum number of iterations."
    max_physical_time: float
    "Maximum physical time for transient simulations."
    max_inner_iterations: int
    "Maximum number of inner iterations for implicit-time transient simulations."
    stop_on_any: bool
    "If true, stop the simulation when any stopping condition is met. Otherwise, stop when all stopping conditions are met."

    @classmethod
    def _from_proto(cls, proto: stopcondpb.BasicStoppingConditions) -> "GeneralStoppingConditions":
        stop_on_any = proto.op == outputpb.STOP_COND_OP_ANY
        return cls(
            max_iterations=proto.max_iterations,
            max_physical_time=proto.max_physical_time,
            max_inner_iterations=proto.max_inner_iterations,
            stop_on_any=stop_on_any,
        )


def list_stopping_conditions(simulation_template_id: str) -> list[StoppingCondition]:
    """
    List all stopping conditions for a simulation template.

    Parameters
    ----------
    simulation_template_id : str
        Simulation template for which to list the stopping conditions.
    """
    req = stopcondpb.ListStoppingConditionsRequest(simulation_template_id=simulation_template_id)
    res = get_default_client().ListStoppingConditions(req)
    return [StoppingCondition._from_proto(sc) for sc in res.stopping_conditions]


def get_stopping_condition(simulation_template_id: str, id: str) -> StoppingCondition:
    """
    Get a stopping condition.

    Parameters
    ----------
    simulation_template_id : str
        Simulation template for which to get the stopping condition.
    id : str
        ID of the stopping condition to get.
    """
    req = stopcondpb.GetStoppingConditionRequest(
        simulation_template_id=simulation_template_id, id=id
    )
    res = get_default_client().GetStoppingCondition(req)
    return StoppingCondition._from_proto(res.stopping_condition)


def create_or_update_stopping_condition(
    simulation_template_id: str,
    output_definition_id: str,
    threshold: float,
    start_at_iteration: int | None = None,
    averaging_iterations: int | None = None,
    iterations_to_consider: int | None = None,
) -> StoppingCondition:
    """
    Create a stopping condition on an output definition, or update it if the stopping condition
    already has one.

    While this API will prevent the creation of multiple stopping conditions on the same output
    definition, the UI does not. If this endpoint is invoked with an output definition that has
    multiple stopping conditions, all but one will be deleted, and the remaining one will be
    updated.

    Parameters
    ----------
    simulation_template_id : str
        ID of the simulation template for which to create the stopping condition.
    output_definition_id : str
        ID of the output definition on which the stopping condition is based.
    threshold : float
        Threshold for the stopping condition.
        For a residual stopping condition, the condition is met when the residual drops below
        this threshold.  For a non-residual-based stopping condition, the condition is met when the
        moving average in the monitored output deviates by less than this percentage of its current
        moving average over the specified number of iterations.
    start_at_iteration : int, optional
        The condition will evaluate to false before this iteration is reached. Default: 1.
    averaging_iterations : int, optional
        Trailing average window length. Number of iterations over which the monitored value is
        averaged before the threshold check is applied. Default: 1.
    iterations_to_consider : int, optional
        Number of (averaged) iterations to consider when determining maximum percent
        deviation from the current value. Default: 1.
    """
    req = stopcondpb.CreateOrUpdateStoppingConditionRequest(
        simulation_template_id=simulation_template_id,
        output_definition_id=output_definition_id,
        threshold=threshold,
        start_at_iteration=start_at_iteration,
        averaging_iterations=averaging_iterations,
        iterations_to_consider=iterations_to_consider,
    )
    res = get_default_client().CreateOrUpdateStoppingCondition(req)
    return StoppingCondition._from_proto(res.stopping_condition)


def delete_stopping_condition(simulation_template_id: str, id: str) -> None:
    """
    Delete a stopping condition.

    Parameters
    ----------
    simulation_template_id : str
        Simulation template in which to delete the stopping condition.
    id : str
        ID of the stopping condition to delete.
    """
    req = stopcondpb.DeleteStoppingConditionRequest(
        simulation_template_id=simulation_template_id, id=id
    )
    get_default_client().DeleteStoppingCondition(req)


def get_general_stopping_conditions(simulation_template_id: str) -> GeneralStoppingConditions:
    """
    Get the general stopping conditions for a simulation template.

    .. warning:: This feature is experimental and may change or be removed without notice.

    Parameters
    ----------
    simulation_template_id : str
        Simulation template for which to get the general stopping conditions.
    """
    req = stopcondpb.GetBasicStoppingConditionsRequest(
        simulation_template_id=simulation_template_id
    )
    res = get_default_client().GetBasicStoppingConditions(req)
    return GeneralStoppingConditions._from_proto(res.basic_stopping_conditions)


def update_general_stopping_conditions(
    simulation_template_id: str,
    max_iterations: int | None = None,
    max_physical_time: float | None = None,
    max_inner_iterations: int | None = None,
    stop_on_any: bool | None = None,
) -> GeneralStoppingConditions:
    """
    Update the general stopping conditions for a simulation template.

    .. warning:: This feature is experimental and may change or be removed without notice.

    Parameters
    ----------
    simulation_template_id : str
        Simulation template for which to update the general stopping conditions.
    max_iterations : int, optional
        Maximum number of iterations.
    max_physical_time : float, optional
        Maximum physical time for transient simulations.
    max_inner_iterations : int, optional
        Maximum number of inner iterations for implicit-time transient simulations.
    stop_on_any : bool, optional
        If true, stop the simulation when any stopping condition is met. Otherwise, stop when all
        stopping conditions are met. Default: false.
    """
    op = outputpb.INVALID_STOP_COND_OP
    if stop_on_any == True:
        op = outputpb.STOP_COND_OP_ANY
    elif stop_on_any == False:
        op = outputpb.STOP_COND_OP_ALL

    req = stopcondpb.UpdateBasicStoppingConditionsRequest(
        simulation_template_id=simulation_template_id,
        max_iterations=max_iterations,
        max_physical_time=max_physical_time,
        max_inner_iterations=max_inner_iterations,
        op=op,
    )
    res = get_default_client().UpdateBasicStoppingConditions(req)
    return GeneralStoppingConditions._from_proto(res.basic_stopping_conditions)


@dataclass
class StoppingConditionResult:
    """
    Result of evaluating a single stopping condition.

    Attributes
    ----------
    output_name : str
        Name of the output being monitored.
    threshold : float
        The threshold value for this condition.
    value : float
        The actual value of the monitored output.
    satisfied : bool
        Whether this condition was satisfied.
    is_force_condition : bool
        Whether this is a force-stop condition (e.g., max iterations, max time).
        Force conditions cause immediate termination regardless of other conditions.
    """

    output_name: str
    threshold: float
    value: float
    satisfied: bool
    is_force_condition: bool


@dataclass
class StoppingConditionStatusResult:
    """
    Status of all stopping conditions for a simulation.

    This represents the evaluation of stopping conditions against the final
    simulation results.

    Attributes
    ----------
    overall_success : bool
        Whether the overall stopping criteria were met (excluding force-stop conditions).
    force_stopped : bool
        Whether a force-stop condition was triggered.
    condition_results : list[StoppingConditionResult]
        Results for each individual stopping condition.
    """

    overall_success: bool
    force_stopped: bool
    condition_results: list[StoppingConditionResult]

    @classmethod
    def _from_proto(
        cls, proto: simulationpb.GetStoppingConditionStatusResponse
    ) -> "StoppingConditionStatusResult":
        condition_results = []
        for i, condition in enumerate(proto.conditions):
            # Get the value from the status with bounds checking
            value = (
                proto.status.value[i].values[0].value
                if i < len(proto.status.value) and proto.status.value[i].values
                else float("nan")
            )

            # Get the threshold, checking for field presence (not truthiness)
            threshold = condition.threshold.value if condition.HasField("threshold") else 0.0

            # Check if this is a force condition
            is_force = condition.op == outputpb.STOP_COND_OP_FORCE

            # Get output name with field presence check
            output_name = condition.output.name if condition.HasField("output") else ""

            # Get satisfied status with bounds checking
            satisfied = (
                proto.status.cond_success[i] if i < len(proto.status.cond_success) else False
            )

            condition_results.append(
                StoppingConditionResult(
                    output_name=output_name,
                    threshold=threshold,
                    value=value,
                    satisfied=satisfied,
                    is_force_condition=is_force,
                )
            )

        return cls(
            overall_success=proto.status.success,
            force_stopped=proto.status.force_stop,
            condition_results=condition_results,
        )

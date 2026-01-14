from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Type, Mapping

if TYPE_CHECKING:
    from .core import Stage


class PipelineInput:
    """
    A named input for a Stage. Explicitly connected to a PipelineOutput.
    """

    def __init__(self, upstream_output: "PipelineOutput", owner: "Stage", name: str):
        self.upstream_output = upstream_output
        self.owner = owner
        self.name = name

    def _to_dict(self, id_for_stage: dict) -> dict:
        if self.upstream_output.owner not in id_for_stage:
            raise ValueError(
                f"Stage {self.owner} depends on a stage, {self.upstream_output.owner}, that isn't in the Pipeline. Did you forget to add it?"
            )
        upstream_stage_id = id_for_stage[self.upstream_output.owner]
        upstream_output_name = self.upstream_output.name
        return {self.name: f"{upstream_stage_id}.{upstream_output_name}"}


class PipelineOutput(ABC):
    """
    A named output for a Stage. Can be used to spawn any number of connected PipelineInputs.
    """

    def __init__(self, owner: "Stage", name: str):
        self.owner = owner
        self.name = name
        self.downstream_inputs: list[PipelineInput] = []

    def _spawn_input(self, owner: "Stage", name: str) -> PipelineInput:
        input = PipelineInput(self, owner, name)
        self.downstream_inputs.append(input)
        return input


# Concrete PipelineOutput classes, i.e. the things that can "flow" in a Pipeline


class PipelineOutputGeometry(PipelineOutput):
    """A representation of a Geometry in a Pipeline."""

    pass


class PipelineOutputMesh(PipelineOutput):
    """A representation of a Mesh in a Pipeline."""

    pass


class PipelineOutputSimulation(PipelineOutput):
    """A representation of a Simulation in a Pipeline."""

    pass


# We don't inherit from StrEnum because that was added in Python 3.11, but we still want to support
# older versions. Inheriting from str and Enum gives us the StrEnum-like behavior we want.
class FlowableType(str, Enum):
    """Canonical flowable type identifiers."""

    GEOMETRY = "Geometry"
    MESH = "Mesh"
    SIMULATION = "Simulation"

    def __str__(self) -> str:
        return self.value


_FLOWABLE_NAME_TO_CLASS: dict[FlowableType, Type[PipelineOutput]] = {
    FlowableType.GEOMETRY: PipelineOutputGeometry,
    FlowableType.MESH: PipelineOutputMesh,
    FlowableType.SIMULATION: PipelineOutputSimulation,
}


def flowable_class_to_name(output_cls: Type[PipelineOutput]) -> FlowableType:
    """
    Convert a PipelineOutput subclass to the canonical flowable type name used in pipeline YAML.
    """
    for flowable_type, cls in _FLOWABLE_NAME_TO_CLASS.items():
        if issubclass(output_cls, cls):
            return flowable_type
    raise ValueError(f"Unsupported PipelineOutput subclass: {output_cls.__name__}")


def flowable_name_to_class(name: str | FlowableType) -> Type[PipelineOutput]:
    """
    Convert a canonical flowable type name into the corresponding PipelineOutput subclass.
    """
    try:
        flowable_type = FlowableType(name)
    except ValueError as exc:
        supported = ", ".join(ft.value for ft in FlowableType)
        raise ValueError(
            f"Unknown flowable type '{name}'. Supported types are: {supported}"
        ) from exc
    return _FLOWABLE_NAME_TO_CLASS[flowable_type]


def _ensure_flowable_mapping(data: Mapping[str, FlowableType | str]) -> dict[str, FlowableType]:
    mapping: dict[str, FlowableType] = {}
    for name, value in data.items():
        mapping[name] = value if isinstance(value, FlowableType) else FlowableType(value)
    return mapping


@dataclass(slots=True)
class FlowableIOSchema:
    """Typed representation of RunScript input/output schema."""

    inputs: dict[str, FlowableType] = field(default_factory=dict)
    outputs: dict[str, FlowableType] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Mapping[str, FlowableType | str]]) -> "FlowableIOSchema":
        return cls(
            inputs=_ensure_flowable_mapping(data["inputs"]),
            outputs=_ensure_flowable_mapping(data["outputs"]),
        )

    def to_dict(self) -> dict[str, dict[str, str]]:
        return {
            "inputs": {name: flowable.value for name, flowable in self.inputs.items()},
            "outputs": {name: flowable.value for name, flowable in self.outputs.items()},
        }

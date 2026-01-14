# Copyright 2025 Luminary Cloud, Inc. All Rights Reserved.
from dataclasses import dataclass, field
from typing import List, Optional, Union, TYPE_CHECKING
from datetime import datetime

from google.protobuf.struct_pb2 import Struct
from google.protobuf.json_format import ParseDict

from ..enum import QuantityType
from .._client import get_default_client
from .._proto.api.v0.luminarycloud.physics_ai import physics_ai_pb2 as physaipb
from .._wrapper import ProtoWrapper, ProtoWrapperBase

if TYPE_CHECKING:
    from ..solution import Solution


@dataclass(kw_only=True)
class ExportConfig:
    """
    Configuration for exporting Physics AI dataset cases.

    .. warning:: This feature is experimental and may change or be removed without notice.

    Parameters
    ----------
    exclude_surfaces : List[str], optional
        Raw mesh boundary names to exclude from export.
    exclude_tags : List[str], optional
        Geometry tag names to exclude. These are resolved to mesh boundary names
        server-side based on the geometry tags.
    fill_holes : float, optional
        Size threshold for filling holes in the surface mesh. Default is 0 (no filling).
    single_precision : bool, optional
        If True, export floating point fields in single precision. Default is True.
    process_volume : bool, optional
        If True, include volume mesh data in the export. Default is False.
    surface_fields_to_keep : List[QuantityType], optional
        Surface fields to include in the export. If empty, all fields are kept.
    volume_fields_to_keep : List[QuantityType], optional
        Volume fields to include in the export. If empty, all fields are kept.
    """

    exclude_surfaces: List[str] = field(default_factory=list)
    exclude_tags: List[str] = field(default_factory=list)
    fill_holes: float = 0.0
    single_precision: bool = True
    process_volume: bool = False
    surface_fields_to_keep: List[QuantityType] = field(default_factory=list)
    volume_fields_to_keep: List[QuantityType] = field(default_factory=list)


@dataclass
class DatasetCaseInput:
    """
    Input for a case in a Physics AI dataset.

    .. warning:: This feature is experimental and may change or be removed without notice.

    Parameters
    ----------
    solution : Solution
        The solution to include in the dataset.
    params : dict, optional
        Physics parameters for this case (e.g., {"alpha": 5.0, "stream_velocity": 50.0}).
        These are used as conditioning inputs during training.
    """

    solution: "Solution"
    params: dict = field(default_factory=dict)


@ProtoWrapper(physaipb.PhysicsAiDatasetCase)
class PhysicsAiDatasetCase(ProtoWrapperBase):
    """
    Represents a case in a Physics AI dataset.

    .. warning:: This feature is experimental and may change or be removed without notice.
    """

    case_id: str
    solution_id: str
    simulation_id: str
    _proto: physaipb.PhysicsAiDatasetCase


@ProtoWrapper(physaipb.PhysicsAiDataset)
class PhysicsAiDataset(ProtoWrapperBase):
    """
    Represents a Physics AI dataset containing training cases.

    .. warning:: This feature is experimental and may change or be removed without notice.
    """

    id: str
    created_by: str
    name: str
    description: str
    is_locked: bool
    creation_time: datetime
    update_time: datetime
    _proto: physaipb.PhysicsAiDataset


def create_dataset(
    name: str,
    cases: List[Union["Solution", DatasetCaseInput]],
    export_config: Optional[ExportConfig] = None,
    description: str = "",
    parameter_schema: Optional[dict] = None,
) -> PhysicsAiDataset:
    """
    Create a Physics AI dataset from simulation solutions.

    .. warning:: This feature is experimental and may change or be removed without notice.

    Parameters
    ----------
    name : str
        Name of the dataset
    cases : List[Union[Solution, DatasetCaseInput]]
        List of solutions or DatasetCaseInput objects. For simple cases, pass
        Solution objects directly. For cases with physics parameters (e.g., alpha,
        stream_velocity), wrap in DatasetCaseInput.
    export_config : ExportConfig, optional
        Export configuration. If not provided, uses defaults (single_precision=True).
    description : str, optional
        Description of the dataset
    parameter_schema : dict, optional
        JSON schema for case parameters

    Returns
    -------
    PhysicsAiDataset
        The created dataset

    Examples
    --------
    Simple usage with solutions (uses default export config):

    >>> dataset = create_dataset(
    ...     name="my-dataset",
    ...     cases=[solution1, solution2, solution3],
    ... )

    With custom export config:

    >>> dataset = create_dataset(
    ...     name="my-dataset",
    ...     cases=[solution1, solution2, solution3],
    ...     export_config=ExportConfig(
    ...         exclude_tags=["Farfield", "Symmetry"],
    ...         surface_fields_to_keep=[QuantityType.PRESSURE, QuantityType.WALL_SHEAR_STRESS],
    ...     ),
    ... )

    With physics parameters:

    >>> dataset = create_dataset(
    ...     name="parametric-dataset",
    ...     cases=[
    ...         DatasetCaseInput(solution1, params={"alpha": 5.0}),
    ...         DatasetCaseInput(solution2, params={"alpha": 10.0}),
    ...     ],
    ...     export_config=ExportConfig(process_volume=True),
    ... )
    """
    # Use default export config if not provided
    if export_config is None:
        export_config = ExportConfig()

    # Build case inputs
    case_inputs = []
    for case in cases:
        if isinstance(case, DatasetCaseInput):
            solution = case.solution
            params = case.params
        else:
            # It's a Solution object
            solution = case
            params = {}

        case_input = physaipb.CreatePhysicsAiDatasetCaseInput(
            solution_id=solution.id,
            simulation_id=solution.simulation_id,
        )
        if params:
            case_input.params.CopyFrom(ParseDict(params, Struct()))
        case_inputs.append(case_input)

    # Build export config proto from dataclass
    export_config_proto = physaipb.GetSolutionDataPhysicsAIRequest(
        exclude_surfaces=export_config.exclude_surfaces,
        exclude_tags=export_config.exclude_tags,
        fill_holes=export_config.fill_holes,
        single_precision=export_config.single_precision,
        process_volume=export_config.process_volume,
    )
    if export_config.surface_fields_to_keep:
        export_config_proto.surface_fields_to_keep.extend(export_config.surface_fields_to_keep)
    if export_config.volume_fields_to_keep:
        export_config_proto.volume_fields_to_keep.extend(export_config.volume_fields_to_keep)

    # Build parameter schema
    if parameter_schema:
        param_schema_proto = ParseDict(parameter_schema, Struct())
    else:
        # Default empty schema
        param_schema_proto = Struct()

    req = physaipb.CreateDatasetRequest(
        name=name,
        description=description,
        cases=case_inputs,
        parameter_schema=param_schema_proto,
        export_config=export_config_proto,
    )

    response = get_default_client().CreateDataset(req)
    return PhysicsAiDataset(response.dataset)


def list_datasets() -> List[PhysicsAiDataset]:
    """
    List Physics AI datasets accessible to the current user.

    Returns datasets created by the current user plus platform-curated datasets.

    .. warning:: This feature is experimental and may change or be removed without notice.

    Returns
    -------
    List[PhysicsAiDataset]
        A list of accessible Physics AI datasets, ordered by creation time (newest first).

    Examples
    --------
    List all datasets:

    >>> datasets = list_datasets()
    >>> for ds in datasets:
    ...     print(f"{ds.name}: {ds.id} (locked={ds.is_locked})")
    """
    req = physaipb.ListDatasetsRequest()
    response = get_default_client().ListDatasets(req)
    return [PhysicsAiDataset(dataset) for dataset in response.datasets]

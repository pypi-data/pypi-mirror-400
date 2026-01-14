# File: python/sdk/luminarycloud/inference/inference.py
# Copyright 2025 Luminary Cloud, Inc. All Rights Reserved.
from typing import Any
from enum import IntEnum
from google.protobuf.json_format import MessageToDict
from .._wrapper import ProtoWrapper, ProtoWrapperBase
from .._proto.api.v0.luminarycloud.physicsaiinference import (
    physicsaiinference_pb2 as physicsaiinferencepb,
)
from .._proto.base import base_pb2 as basepb


class VisualizationOutput(IntEnum):
    """
    Represents the type of visualization output.

    Attributes
    ----------
    INVALID
        Invalid visualization output type.
    LUMINARY
        Luminary visualization format.
    VTK
        VTK visualization format.
    """

    INVALID = physicsaiinferencepb.INVALID
    LUMINARY = physicsaiinferencepb.LUMINARY
    VTK = physicsaiinferencepb.VTK


class InferenceFieldType(IntEnum):
    """
    Represents the type of an inference field.

    Attributes
    ----------
    UNKNOWN_TYPE
        Unknown field type.
    SCALAR
        Scalar field type (single value).
    VECTOR
        Vector field type (multiple values).
    """

    UNKNOWN_TYPE = physicsaiinferencepb.UNKNOWN_TYPE
    SCALAR = physicsaiinferencepb.SCALAR
    VECTOR = physicsaiinferencepb.VECTOR


class InferenceFieldCategory(IntEnum):
    """
    Represents the category of an inference field.

    Attributes
    ----------
    UNKNOWN_CATEGORY
        Unknown field category.
    NUMERIC
        Numeric field category (e.g., forces, moments).
    SURFACE
        Surface field category (e.g., surface pressure).
    VOLUME
        Volume field category (e.g., velocity, pressure).
    """

    UNKNOWN_CATEGORY = physicsaiinferencepb.UNKNOWN_CATEGORY
    NUMERIC = physicsaiinferencepb.NUMERIC
    SURFACE = physicsaiinferencepb.SURFACE
    VOLUME = physicsaiinferencepb.VOLUME


@ProtoWrapper(physicsaiinferencepb.VisualizationExport)
class VisualizationExport(ProtoWrapperBase):
    """Represents a visualization export."""

    type: VisualizationOutput
    url: str
    _proto: physicsaiinferencepb.VisualizationExport

    def get_url(self) -> str:
        return self.url


@ProtoWrapper(physicsaiinferencepb.NumericResult)
class NumericResult(ProtoWrapperBase):
    """Represents a numeric result."""

    scalar: float
    vector: list[float]
    _proto: physicsaiinferencepb.NumericResult

    def get_value(self) -> Any:
        if self._proto.HasField("scalar"):
            return self.scalar
        if self._proto.HasField("vector"):
            return list(self._proto.vector.values)
        return None


@ProtoWrapper(physicsaiinferencepb.SurfaceForInference)
class SurfaceForInference(ProtoWrapperBase):
    """Represents a surface for inference."""

    name: str
    url: str
    _proto: physicsaiinferencepb.SurfaceForInference

    def get_name(self) -> str:
        return self.name

    def get_url(self) -> str:
        return self.url


@ProtoWrapper(physicsaiinferencepb.InferenceResult)
class InferenceResult(ProtoWrapperBase):
    """Represents an inference result."""

    name: str
    surface_results: dict[str, str]
    volume_results: dict[str, str]
    visualizations: list[VisualizationExport]

    @property
    def number_outputs(self) -> dict[str, NumericResult]:
        """Returns number_outputs with wrapped NumericResult values."""
        return {k: NumericResult(v) for k, v in self._proto.number_outputs.items()}

    def get_number_outputs(self) -> dict[str, Any]:
        return MessageToDict(self._proto.number_outputs, preserving_proto_field_name=True)

    def get_surface_results(self) -> dict[str, Any]:
        return MessageToDict(self.surface_results, preserving_proto_field_name=True)

    def get_volume_results(self) -> dict[str, Any]:
        return MessageToDict(self.volume_results, preserving_proto_field_name=True)

    def get_visualizations(self) -> list[dict[str, Any]]:
        return [
            MessageToDict(viz._proto, preserving_proto_field_name=True)
            for viz in self.visualizations
        ]


@ProtoWrapper(physicsaiinferencepb.InferenceServiceJob)
class InferenceJob(ProtoWrapperBase):
    """Represents an inference service job."""

    job_id: str
    status: basepb.JobStatus
    results: list[InferenceResult]
    merged_visualizations: list[VisualizationExport]
    _proto: physicsaiinferencepb.InferenceServiceJob

    @property
    def id(self) -> str:
        """Alias for job_id for convenience."""
        return self.job_id

    def get_status(self) -> str:
        return basepb.JobStatusType.Name(self.status.typ)

    def get_results(self) -> list[dict[str, Any]]:
        return [
            MessageToDict(result._proto, preserving_proto_field_name=True)
            for result in self.results
        ]

    def get_merged_visualizations(self) -> list[dict[str, Any]]:
        return [
            MessageToDict(viz._proto, preserving_proto_field_name=True)
            for viz in self.merged_visualizations
        ]


@ProtoWrapper(physicsaiinferencepb.InferenceField)
class InferenceField(ProtoWrapperBase):
    """Represents an inference field."""

    name: str
    type: InferenceFieldType
    category: InferenceFieldCategory
    _proto: physicsaiinferencepb.InferenceField

# Copyright 2025 Luminary Cloud, Inc. All Rights Reserved.
from typing import Any, Dict, Optional
from json import dumps as json_dumps
import os
import uuid
from .._client import get_default_client
from .._proto.api.v0.luminarycloud.physicsaiinference import (
    physicsaiinference_pb2 as physicsaiinferencepb,
)
from .upload import upload_file, uploadpb
from ..types import PhysicsAiModelVersionID, PhysicsAiInferenceJobID
from ..physics_ai.inference import VisualizationExport, InferenceJob, SurfaceForInference


# Helper function to upload an STL file if it is not a GCS URL
def _upload_if_file(project_id: str, fname: str) -> str:
    if not fname.split(".")[-1].lower() == "stl":
        raise RuntimeError("Unsupported file for inference")
    if fname.startswith("gs://"):
        return fname
    if os.path.exists(fname) and os.path.isfile(fname):
        params = uploadpb.ResourceParams()
        client = get_default_client()
        result = upload_file(client, project_id, params, fname)
        return result[1].url
    raise RuntimeError("Unsupported file for inference")


def _build_inference_request(
    project_id: str,
    geometry: str,
    model_version_id: PhysicsAiModelVersionID,
    conditions: Optional[Dict[str, Any]] = None,
    settings: Optional[Dict[str, Any]] = None,
    surfaces: Optional[list[SurfaceForInference]] = None,
    inference_fields: Optional[list[str]] = None,
    per_surface_visualizations: Optional[list[VisualizationExport]] = None,
    merged_visualizations: Optional[list[VisualizationExport]] = None,
) -> physicsaiinferencepb.CreateInferenceServiceJobRequest:
    """Helper function to build an inference service job request.

    Parameters
    ----------
    project_id : str
        Reference to a project.
    geometry : str
        Path to STL file or GCS URL (gs://) of the geometry to run inference on.
        If a local file path is provided, it will be uploaded to the project.
    model_version_id : PhysicsAiModelVersionID
        The ID of the trained model version to use for inference.
    conditions : Dict[str, Any], optional
        Dictionary of conditions to be passed to the inference service (e.g., alpha, beta, etc.).
    settings : Dict[str, Any], optional
        Dictionary of settings to be passed to inference service (e.g., stencil_size)
    surfaces : list[SurfaceForInference], optional
        List of surfaces for inference, each with 'name' and 'url' keys.
    inference_fields : list[str], optional
        Specific fields within the trained model to return inference results for.
    per_surface_visualizations : list[VisualizationExport], optional
        Types of visualization to write for each surface (e.g., LUMINARY, VTK).
    merged_visualizations : list[VisualizationExport], optional
        Types of merged visualization to write across all surfaces.

    Returns
    -------
    CreateInferenceServiceJobRequest
        The constructed protobuf request object.
    """

    geometry_url = _upload_if_file(project_id, geometry)

    # Embed settings and store as bytes
    settings_bytes = b""
    if settings is not None:
        settings_bytes = json_dumps(settings).encode("utf-8")

    # Convert parameters dict to bytes if provided
    conditions_bytes = b""
    if conditions is not None:
        conditions_bytes = json_dumps(conditions).encode("utf-8")

    # Generate a unique request_id for deduplication and to satisfy the database constraint
    # The backend uses request_id as the Name field, which must be non-empty
    request_id = str(uuid.uuid4())

    # Build request with base parameters
    req_params = {
        "request_id": request_id,
        "geometry": geometry_url,
        "model_version_id": str(model_version_id),
        "conditions": conditions_bytes,
        "settings": settings_bytes,
        "project_id": project_id,
    }

    # Add optional inference fields
    if inference_fields is not None:
        req_params["inference_fields"] = inference_fields

    # Add optional per-surface visualizations
    if per_surface_visualizations is not None:
        req_params["per_surface_visualizations"] = per_surface_visualizations

    # Add optional merged visualizations
    if merged_visualizations is not None:
        req_params["merged_visualizations"] = merged_visualizations

    # Add optional surfaces
    if surfaces is not None:
        surfaces_proto: list[physicsaiinferencepb.SurfaceForInference] = []
        for surface in surfaces:
            surfaces_proto.append(
                physicsaiinferencepb.SurfaceForInference(
                    name=surface["name"], url=_upload_if_file(project_id, surface["url"])
                )
            )
        req_params["surfaces"] = surfaces_proto

    return physicsaiinferencepb.CreateInferenceServiceJobRequest(**req_params)


def create_inference_job(
    project_id: str,
    geometry: str,
    model_version_id: PhysicsAiModelVersionID,
    synchronous: bool = False,
    conditions: Optional[Dict[str, Any]] = None,
    settings: Optional[Dict[str, Any]] = None,
    surfaces: Optional[list[SurfaceForInference]] = None,
    inference_fields: Optional[list[str]] = None,
    per_surface_visualizations: Optional[list[VisualizationExport]] = None,
    merged_visualizations: Optional[list[VisualizationExport]] = None,
) -> InferenceJob:
    """Creates a synchronous inference service job.

    Parameters
    ----------
    project_id : str
        Reference to a project.
    geometry : str
        Path to STL file or GCS URL (gs://) of the geometry to run inference on.
        If a local file path is provided, it will be uploaded to the project.
    model_version_id : PhysicsAiModelVersionID
        The ID of the trained model version to use for inference.
    synchronous: bool = False,
        Whether to wait for the job to complete before returning the result.
    conditions : Dict[str, Any], optional
        Dictionary of conditions to be passed to the inference service (e.g., alpha, beta, etc.).
    settings : Dict[str, Any], optional
        Dictionary of settings to be passed to inference service (e.g., stencil_size)
    surfaces : list[SurfaceForInference], optional
        List of surfaces for inference, each with 'name' and 'url' keys.
    inference_fields : list[str], optional
        Specific fields within the trained model to return inference results for.
    per_surface_visualizations : list[VisualizationOutput], optional
        Types of visualization to write for each surface (e.g., LUMINARY, VTK).
    merged_visualizations : list[VisualizationOutput], optional
        Types of merged visualization to write across all surfaces.

    Returns
    -------
    dict[str, Any]
        Response from the server containing results, with keys mapping to:
        - Numeric results: float/vector values
        - Surface/volume results: URLs to data files
        - Visualization results: URLs to visualization files

    warning:: This feature is experimental and may change or be removed without notice.
    """
    req = _build_inference_request(
        project_id,
        geometry,
        model_version_id,
        conditions,
        settings,
        surfaces,
        inference_fields,
        per_surface_visualizations,
        merged_visualizations,
    )
    if synchronous:
        res: physicsaiinferencepb.GetInferenceServiceJobResponse = (
            get_default_client().CreateInferenceServiceJob(req)
        )
    else:  # Asynchronous inference
        res: physicsaiinferencepb.CreateInferenceServiceJobAsyncResponse = (
            get_default_client().CreateInferenceServiceJobAsync(req)
        )
    return InferenceJob(res.job)


def get_inference_job(job_id: str) -> InferenceJob:
    """Retrieves an inference service job by its ID.

    Parameters
    ----------
    job_id : str
        The ID of the inference job to retrieve.

    Returns
    -------
    dict[str, Any]
        The inference job details including results and status.

    warning:: This feature is experimental and may change or be removed without notice.
    """

    req = physicsaiinferencepb.GetInferenceServiceJobRequest(job_id=job_id)
    res: physicsaiinferencepb.GetInferenceServiceJobResponse = (
        get_default_client().GetInferenceServiceJob(req)
    )
    return InferenceJob(res.job)


def list_inference_jobs(project_id: str) -> list[InferenceJob]:
    """Lists all inference service jobs for a project.

    Parameters
    ----------
    project_id : str
        The project to list inference jobs for.
    """
    req = physicsaiinferencepb.ListInferenceServiceJobsRequest(project_id=project_id)
    res: physicsaiinferencepb.ListInferenceServiceJobsResponse = (
        get_default_client().ListInferenceServiceJobs(req)
    )
    return [InferenceJob(job) for job in res.jobs]

# Copyright 2025 Luminary Cloud, Inc. All Rights Reserved.
from typing import List, Optional

from .._client import get_default_client
from .._proto.api.v0.luminarycloud.physics_ai import physics_ai_pb2 as physaipb
from .._proto.api.v0.luminarycloud.physicsaiinference import (
    physicsaiinference_pb2 as physicsaiinferencepb,
)
from .._wrapper import ProtoWrapper, ProtoWrapperBase
from ..types.ids import PhysicsAiModelID, PhysicsAiModelVersionID
from ..enum.physics_ai_lifecycle_state import PhysicsAiLifecycleState


@ProtoWrapper(physaipb.PhysicsAiModelVersion)
class PhysicsAiModelVersion(ProtoWrapperBase):
    """
    Represents a specific version of a Physics AI model.

    .. warning:: This feature is experimental and may change or be removed without notice.
    """

    id: PhysicsAiModelVersionID
    name: str
    lifecycle_state: PhysicsAiLifecycleState
    _proto: physaipb.PhysicsAiModelVersion

    def get_inference_fields(self) -> list[str]:
        """Gets the inference fields available for a trained model version.

        This retrieves the list of output fields that can be requested from a specific
        model version during inference.

        Returns
        -------
        list[str]
            List of available inference field names that can be requested from the model.

        warning:: This feature is experimental and may change or be removed without notice.
        """
        req = physicsaiinferencepb.GetInferenceFieldsRequest(model_version_id=str(self.id))
        res: physicsaiinferencepb.GetInferenceFieldsResponse = (
            get_default_client().GetInferenceFields(req)
        )
        return list(res.inference_fields)


@ProtoWrapper(physaipb.PhysicsAiModel)
class PhysicsAiModel(ProtoWrapperBase):
    """
    Represents a Physics AI model with all its versions.

    .. warning:: This feature is experimental and may change or be removed without notice.
    """

    id: PhysicsAiModelID
    name: str
    description: str
    versions: List[PhysicsAiModelVersion]
    _proto: physaipb.PhysicsAiModel

    def get_latest_version(self) -> Optional[PhysicsAiModelVersion]:
        """
        Get the latest version of this model.

        Returns
        -------
        PhysicsAiModelVersion or None
            The first model version, or None if no versions exist.
            Note: Version ordering is now determined by the backend.
        """
        if not self.versions:
            return None
        return self.versions[0] if self.versions else None


def list_pretrained_models() -> List[PhysicsAiModel]:
    """
    List available pretrained Physics AI models.

    .. warning:: This feature is experimental and may change or be removed without notice.

    Returns
    -------
    list[PhysicsAiModel]
        A list of all available pretrained Physics AI models.
    """
    req = physaipb.ListPretrainedModelsRequest()
    res = get_default_client().ListPretrainedModels(req)
    return [PhysicsAiModel(model) for model in res.models]

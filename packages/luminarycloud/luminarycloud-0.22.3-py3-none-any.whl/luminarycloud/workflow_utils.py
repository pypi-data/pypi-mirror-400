# Copyright 2025 Luminary Cloud, Inc. All Rights Reserved.
"""Utilities for working with workflows and entity IDs."""

from luminarycloud.simulation import _get_workflow_ids
from luminarycloud.types import SimulationID, GeometryID
from luminarycloud._client.client import _get_primary_domain_for_apiserver_domain
import luminarycloud as lc


def get_workflow_url_from_entity(entity_id: str, base_url: str | None = None) -> str:
    """
    Get a complete workflow URL from either a geometry ID or simulation ID.

    The base URL is automatically determined from the current client's API domain.
    For example, if connected to apis.main.int.luminarycloud.com, the URL will use
    https://main.int.luminarycloud.com.


    Parameters
    ----------
    entity_id : str
        Either a geometry ID (starting with 'geo-') or simulation ID (starting with 'sim-')
    base_url : str, optional
        Override the base URL for the Luminary Cloud application. If not provided,
        it will be automatically determined from the client's API domain.

    Returns
    -------
    str
        The complete workflow URL

    Raises
    ------
    ValueError
        If the entity_id is not a valid geometry or simulation ID, or if no simulations
        are found using the specified geometry ID
    """
    # Use the batch function for a single entity
    urls = get_workflow_urls_from_entities([entity_id], base_url)

    if entity_id not in urls:
        if entity_id.startswith("geo-"):
            raise ValueError(f"No simulations found using geometry ID: {entity_id}")
        elif entity_id.startswith("sim-"):
            raise ValueError(f"Unable to resolve simulation ID: {entity_id}")
        else:
            raise ValueError(
                f"Invalid entity ID: {entity_id}. " f"Expected ID starting with 'geo-' or 'sim-'"
            )

    return urls[entity_id]


def get_workflow_urls_from_entities(
    entity_ids: list[str], base_url: str | None = None
) -> dict[str, str]:
    """
    Get workflow URLs for multiple entity IDs in a single batch operation.

    Parameters
    ----------
    entity_ids : list[str]
        List of entity IDs (geometry IDs starting with 'geo-' or simulation IDs
        starting with 'sim-')
    base_url : str, optional
        Override the base URL for the Luminary Cloud application. If not provided,
        it will be automatically determined from the client's API domain.

    Returns
    -------
    dict[str, str]
        Dictionary mapping entity IDs to their workflow URLs. Only includes entity IDs
        that were successfully resolved (partial data pattern).

    Raises
    ------
    ValueError
        If base_url cannot be determined from the client

    Notes
    -----
    - Geometry IDs that don't map to any simulation will be omitted from the result
    - Invalid entity IDs will be omitted from the result
    """
    if not entity_ids:
        return {}

    # Auto-detect base URL from client if not provided
    if base_url is None:
        client = lc.get_default_client()
        # Remove port if present from the API domain
        api_domain = client._apiserver_domain.split(":", maxsplit=1)[0]
        primary_domain = _get_primary_domain_for_apiserver_domain(api_domain)
        if primary_domain is None:
            raise ValueError(f"Unable to determine web URL for API domain: {api_domain}")
        base_url = f"https://{primary_domain}"

    # Separate simulation IDs and geometry IDs
    sim_ids_to_entity: dict[SimulationID, str] = {}
    geo_ids_to_entity: dict[GeometryID, str] = {}

    for entity_id in entity_ids:
        if entity_id.startswith("sim-"):
            sim_ids_to_entity[SimulationID(entity_id)] = entity_id
        elif entity_id.startswith("geo-"):
            geo_ids_to_entity[GeometryID(entity_id)] = entity_id

    # Get project IDs for all simulation IDs
    sim_to_project: dict[SimulationID, str] = {}
    for sim_id in sim_ids_to_entity.keys():
        try:
            sim = lc.get_simulation(sim_id)
            sim_to_project[sim_id] = sim.project_id
        except Exception:
            # Skip simulation IDs that can't be resolved
            continue

    # Handle geometry IDs - find simulations that use each geometry
    for geo_id_typed, entity_id in geo_ids_to_entity.items():
        try:
            geom = lc.get_geometry(geo_id_typed)
            project = geom.project()

            # Find first simulation using this geometry
            for sim in project.list_simulations():
                mesh = lc.get_mesh(sim.mesh_id)
                geom_version = mesh.geometry_version()

                if geom_version and geom_version.geometry().id == entity_id:
                    # Found a simulation using this geometry
                    sim_ids_to_entity[sim.id] = entity_id
                    sim_to_project[sim.id] = project.id
                    break
        except Exception:
            # Skip geometry IDs that can't be resolved
            continue

    # Batch get workflow IDs for all simulation IDs
    result: dict[str, str] = {}
    if sim_ids_to_entity:
        workflow_ids = _get_workflow_ids(list(sim_ids_to_entity.keys()))

        for sim_id, workflow_id in workflow_ids.items():
            entity_id = sim_ids_to_entity[sim_id]
            project_id = sim_to_project.get(sim_id)
            if project_id:
                result[entity_id] = f"{base_url}/project/{project_id}/simulation/{workflow_id}"

    return result

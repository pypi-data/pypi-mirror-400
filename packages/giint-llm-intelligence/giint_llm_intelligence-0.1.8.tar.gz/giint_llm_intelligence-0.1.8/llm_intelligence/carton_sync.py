#!/usr/bin/env python3
"""
GIINT Carton Synchronization Module

Dual-write pattern: GIINT entities are mirrored to Carton knowledge graph.
- JSON = fast operational cache
- Carton = queryable knowledge graph for cross-system integration
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


# ============================================================================
# SCHEMA DESIGN - Concept Naming Conventions
# ============================================================================

def get_project_concept_name(project_id: str) -> str:
    """Get Carton concept name for GIINT project."""
    return f"GIINT_Project_{project_id}"


def get_feature_concept_name(project_id: str, feature_name: str) -> str:
    """Get Carton concept name for GIINT feature."""
    return f"GIINT_Feature_{project_id}_{feature_name}"


def get_component_concept_name(project_id: str, feature_name: str, component_name: str) -> str:
    """Get Carton concept name for GIINT component."""
    return f"GIINT_Component_{project_id}_{feature_name}_{component_name}"


def get_deliverable_concept_name(project_id: str, feature_name: str, component_name: str, deliverable_name: str) -> str:
    """Get Carton concept name for GIINT deliverable."""
    return f"GIINT_Deliverable_{project_id}_{feature_name}_{component_name}_{deliverable_name}"


def get_task_concept_name(project_id: str, feature_name: str, component_name: str, deliverable_name: str, task_id: str) -> str:
    """Get Carton concept name for GIINT task."""
    return f"GIINT_Task_{project_id}_{feature_name}_{component_name}_{deliverable_name}_{task_id}"


# ============================================================================
# CONCEPT CONVERSION - Pydantic Models to Carton Concepts
# ============================================================================

def project_to_concept(project: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert GIINT Project to Carton concept format.

    Args:
        project: Project dict from Pydantic model

    Returns:
        Carton concept data (concept_name, concept, relationships)
    """
    concept_name = get_project_concept_name(project["project_id"])

    # Build description
    description_parts = [
        f"# GIINT Project: {project['project_id']}",
        "",
        f"**Type**: {project.get('project_type', 'single')}",
        f"**Location**: {project['project_dir']}",
        f"**Mode**: {project.get('mode', 'planning')}",
        f"**Created**: {project.get('created_at', 'Unknown')}",
        f"**Updated**: {project.get('updated_at', 'Unknown')}",
        ""
    ]

    if project.get('starlog_path'):
        description_parts.append(f"**STARLOG**: {project['starlog_path']}")

    if project.get('github_repo_url'):
        description_parts.append(f"**GitHub**: {project['github_repo_url']}")

    # Add feature summary
    features = project.get('features', {})
    if features:
        description_parts.extend(["", "## Features"])
        for feature_name in features.keys():
            description_parts.append(f"- {feature_name}")

    # Add sub-projects for composite type
    sub_projects = project.get('sub_projects', [])
    if sub_projects:
        description_parts.extend(["", "## Sub-Projects"])
        for sub_project_id in sub_projects:
            description_parts.append(f"- {sub_project_id}")

    concept = "\n".join(description_parts)

    # Build relationships
    relationships = [
        {"relationship": "is_a", "related": ["GIINT_Project"]},
        {"relationship": "has_personal_domain", "related": ["frameworks"]},
        {"relationship": "has_actual_domain", "related": ["Project_Management"]}
    ]

    # Add relationships to sub-projects (for composite projects)
    for sub_project_id in sub_projects:
        relationships.append({
            "relationship": "has_sub_project",
            "related": [get_project_concept_name(sub_project_id)]
        })

    return {
        "concept_name": concept_name,
        "concept": concept,
        "relationships": relationships
    }


def feature_to_concept(project_id: str, feature_name: str, feature: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert GIINT Feature to Carton concept format.

    Args:
        project_id: Parent project ID
        feature_name: Feature name
        feature: Feature dict from Pydantic model

    Returns:
        Carton concept data
    """
    concept_name = get_feature_concept_name(project_id, feature_name)

    # Build description
    description_parts = [
        f"# GIINT Feature: {feature_name}",
        "",
        f"**Project**: {project_id}",
        f"**Created**: {feature.get('created_at', 'Unknown')}",
        ""
    ]

    # Add spec info if exists
    spec = feature.get('spec')
    if spec:
        description_parts.extend([
            "## Specification",
            f"**File**: {spec.get('spec_file_path', 'None')}",
            f"**Status**: {spec.get('status', 'draft')}",
            f"**Created**: {spec.get('created_at', 'Unknown')}",
            ""
        ])

    # Add component summary
    components = feature.get('components', {})
    if components:
        description_parts.extend(["## Components"])
        for component_name in components.keys():
            description_parts.append(f"- {component_name}")

    concept = "\n".join(description_parts)

    # Build relationships
    relationships = [
        {"relationship": "is_a", "related": ["GIINT_Feature"]},
        {"relationship": "part_of", "related": [get_project_concept_name(project_id)]},
        {"relationship": "has_personal_domain", "related": ["frameworks"]},
        {"relationship": "has_actual_domain", "related": ["Feature_Development"]}
    ]

    return {
        "concept_name": concept_name,
        "concept": concept,
        "relationships": relationships
    }


def component_to_concept(project_id: str, feature_name: str, component_name: str, component: Dict[str, Any]) -> Dict[str, Any]:
    """Convert GIINT Component to Carton concept format."""
    concept_name = get_component_concept_name(project_id, feature_name, component_name)

    description_parts = [
        f"# GIINT Component: {component_name}",
        "",
        f"**Project**: {project_id}",
        f"**Feature**: {feature_name}",
        f"**Created**: {component.get('created_at', 'Unknown')}",
        ""
    ]

    spec = component.get('spec')
    if spec:
        description_parts.extend([
            "## Specification",
            f"**File**: {spec.get('spec_file_path', 'None')}",
            f"**Status**: {spec.get('status', 'draft')}",
            ""
        ])

    deliverables = component.get('deliverables', {})
    if deliverables:
        description_parts.extend(["## Deliverables"])
        for deliverable_name in deliverables.keys():
            description_parts.append(f"- {deliverable_name}")

    concept = "\n".join(description_parts)

    relationships = [
        {"relationship": "is_a", "related": ["GIINT_Component"]},
        {"relationship": "part_of", "related": [get_feature_concept_name(project_id, feature_name)]},
        {"relationship": "has_personal_domain", "related": ["frameworks"]},
        {"relationship": "has_actual_domain", "related": ["Component_Design"]}
    ]

    return {
        "concept_name": concept_name,
        "concept": concept,
        "relationships": relationships
    }


def deliverable_to_concept(project_id: str, feature_name: str, component_name: str, deliverable_name: str, deliverable: Dict[str, Any]) -> Dict[str, Any]:
    """Convert GIINT Deliverable to Carton concept format."""
    concept_name = get_deliverable_concept_name(project_id, feature_name, component_name, deliverable_name)

    description_parts = [
        f"# GIINT Deliverable: {deliverable_name}",
        "",
        f"**Project**: {project_id}",
        f"**Feature**: {feature_name}",
        f"**Component**: {component_name}",
        f"**Created**: {deliverable.get('created_at', 'Unknown')}",
        ""
    ]

    spec = deliverable.get('spec')
    if spec:
        description_parts.extend([
            "## Specification",
            f"**File**: {spec.get('spec_file_path', 'None')}",
            f"**Status**: {spec.get('status', 'draft')}",
            ""
        ])

    tasks = deliverable.get('tasks', {})
    if tasks:
        description_parts.extend(["## Tasks"])
        for task_id, task_data in tasks.items():
            status = task_data.get('status', 'ready')
            assignee = task_data.get('assignee', 'UNKNOWN')
            description_parts.append(f"- {task_id} ({status}, {assignee})")

    operadic_flow_ids = deliverable.get('operadic_flow_ids', [])
    if operadic_flow_ids:
        description_parts.extend(["", "## Vendored OperadicFlows"])
        for flow_id in operadic_flow_ids:
            description_parts.append(f"- {flow_id}")

    concept = "\n".join(description_parts)

    relationships = [
        {"relationship": "is_a", "related": ["GIINT_Deliverable"]},
        {"relationship": "part_of", "related": [get_component_concept_name(project_id, feature_name, component_name)]},
        {"relationship": "has_personal_domain", "related": ["frameworks"]},
        {"relationship": "has_actual_domain", "related": ["Deliverable_Planning"]}
    ]

    return {
        "concept_name": concept_name,
        "concept": concept,
        "relationships": relationships
    }


def task_to_concept(project_id: str, feature_name: str, component_name: str, deliverable_name: str, task_id: str, task: Dict[str, Any]) -> Dict[str, Any]:
    """Convert GIINT Task to Carton concept format."""
    concept_name = get_task_concept_name(project_id, feature_name, component_name, deliverable_name, task_id)

    description_parts = [
        f"# GIINT Task: {task_id}",
        "",
        f"**Project**: {project_id}",
        f"**Feature**: {feature_name}",
        f"**Component**: {component_name}",
        f"**Deliverable**: {deliverable_name}",
        "",
        f"**Status**: {task.get('status', 'ready')}",
        f"**Assignee**: {task.get('assignee', 'UNKNOWN')}",
        f"**Ready**: {task.get('is_ready', False)}",
        f"**Blocked**: {task.get('is_blocked', False)}",
        ""
    ]

    if task.get('agent_id'):
        description_parts.append(f"**Agent ID**: {task['agent_id']}")
    if task.get('human_name'):
        description_parts.append(f"**Human**: {task['human_name']}")
    if task.get('blocked_description'):
        description_parts.append(f"**Block Reason**: {task['blocked_description']}")

    description_parts.append("")

    spec = task.get('spec')
    if spec:
        description_parts.extend([
            "## Specification (Rollup)",
            f"**File**: {spec.get('spec_file_path', 'None')}",
            f"**Status**: {spec.get('status', 'draft')}",
            ""
        ])

    if task.get('github_issue_id'):
        description_parts.extend([
            "## GitHub Integration",
            f"**Issue ID**: {task['github_issue_id']}",
            f"**Issue URL**: {task.get('github_issue_url', 'None')}",
            ""
        ])

    description_parts.extend([
        f"**Created**: {task.get('created_at', 'Unknown')}",
        f"**Updated**: {task.get('updated_at', 'Unknown')}"
    ])

    concept = "\n".join(description_parts)

    relationships = [
        {"relationship": "is_a", "related": ["GIINT_Task"]},
        {"relationship": "part_of", "related": [get_deliverable_concept_name(project_id, feature_name, component_name, deliverable_name)]},
        {"relationship": "has_personal_domain", "related": ["frameworks"]},
        {"relationship": "has_actual_domain", "related": ["Task_Execution"]}
    ]

    # Add status-specific relationships
    status = task.get('status', 'ready')
    if status == 'ready':
        relationships.append({"relationship": "has_status", "related": ["Task_Ready"]})
    elif status == 'in_progress':
        relationships.append({"relationship": "has_status", "related": ["Task_In_Progress"]})
    elif status == 'in_review':
        relationships.append({"relationship": "has_status", "related": ["Task_In_Review"]})
    elif status == 'done':
        relationships.append({"relationship": "has_status", "related": ["Task_Done"]})
    elif status == 'blocked':
        relationships.append({"relationship": "has_status", "related": ["Task_Blocked"]})

    return {
        "concept_name": concept_name,
        "concept": concept,
        "relationships": relationships
    }


# ============================================================================
# SYNC FUNCTIONS - Write to Carton
# ============================================================================

def _add_concept_to_carton(concept_data: Dict[str, Any], desc_update_mode: str = "append") -> Dict[str, Any]:
    """
    Helper function to queue concept to Carton background processor.

    Args:
        concept_data: Dict with concept_name, concept, relationships
        desc_update_mode: How to update if exists (append/prepend/replace)

    Returns:
        Queue result
    """
    try:
        from add_concept_tool import add_observation

        # Format GIINT entity as observation (implementation tag)
        observation_data = {
            "implementation": [{
                "name": concept_data["concept_name"],
                "description": concept_data["concept"],
                "relationships": concept_data["relationships"]
            }],
            "confidence": 1.0
        }

        # Add desc_update_mode to first concept if not default
        if desc_update_mode != "append":
            observation_data["implementation"][0]["desc_update_mode"] = desc_update_mode

        result = add_observation(observation_data)

        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Failed to queue concept to Carton: {e}", exc_info=True)
        return {"error": str(e)}


def sync_project_to_carton(project: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sync GIINT Project to Carton knowledge graph.

    This is the main entry point for syncing an entire project hierarchy.

    Args:
        project: Project dict from Pydantic model

    Returns:
        Sync result with success status
    """
    try:
        project_id = project["project_id"]
        logger.info(f"Starting Carton sync for project: {project_id}")

        # 1. Sync project itself
        project_concept = project_to_concept(project)
        result = _add_concept_to_carton(project_concept)

        if "error" in str(result).lower() and "already exists" not in str(result).lower():
            logger.error(f"Failed to sync project: {result}")
            return {"success": False, "error": f"Failed to sync project: {result}"}

        # 2. Sync all features (and recursively their children)
        features = project.get("features", {})
        for feature_name, feature_data in features.items():
            sync_feature_to_carton(project_id, feature_name, feature_data)

        logger.info(f"Successfully synced project {project_id} to Carton")
        return {
            "success": True,
            "project_id": project_id,
            "synced_features": len(features)
        }

    except Exception as e:
        logger.error(f"Failed to sync project to Carton: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


def sync_feature_to_carton(project_id: str, feature_name: str, feature: Dict[str, Any]) -> Dict[str, Any]:
    """Sync GIINT Feature to Carton."""
    try:
        # Sync feature concept only
        feature_concept = feature_to_concept(project_id, feature_name, feature)
        _add_concept_to_carton(feature_concept)

        return {"success": True, "feature_name": feature_name}

    except Exception as e:
        logger.error(f"Failed to sync feature {feature_name}: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


def sync_component_to_carton(project_id: str, feature_name: str, component_name: str, component: Dict[str, Any]) -> Dict[str, Any]:
    """Sync GIINT Component to Carton."""
    try:
        # Sync component concept only
        component_concept = component_to_concept(project_id, feature_name, component_name, component)
        _add_concept_to_carton(component_concept)

        return {"success": True, "component_name": component_name}

    except Exception as e:
        logger.error(f"Failed to sync component {component_name}: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


def sync_deliverable_to_carton(project_id: str, feature_name: str, component_name: str, deliverable_name: str, deliverable: Dict[str, Any]) -> Dict[str, Any]:
    """Sync GIINT Deliverable to Carton."""
    try:
        # Sync deliverable concept only
        deliverable_concept = deliverable_to_concept(project_id, feature_name, component_name, deliverable_name, deliverable)
        _add_concept_to_carton(deliverable_concept)

        return {"success": True, "deliverable_name": deliverable_name}

    except Exception as e:
        logger.error(f"Failed to sync deliverable {deliverable_name}: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


def sync_task_to_carton(project_id: str, feature_name: str, component_name: str, deliverable_name: str, task_id: str, task: Dict[str, Any]) -> Dict[str, Any]:
    """Sync GIINT Task to Carton."""
    try:
        task_concept = task_to_concept(project_id, feature_name, component_name, deliverable_name, task_id, task)
        _add_concept_to_carton(task_concept)
        return {"success": True, "task_id": task_id}

    except Exception as e:
        logger.error(f"Failed to sync task {task_id}: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


def update_task_in_carton(project_id: str, feature_name: str, component_name: str, deliverable_name: str, task_id: str, task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing task in Carton.

    Uses desc_update_mode="replace" to update the task concept with new status/metadata.
    """
    try:
        task_concept = task_to_concept(project_id, feature_name, component_name, deliverable_name, task_id, task)
        _add_concept_to_carton(task_concept, desc_update_mode="replace")
        logger.info(f"Updated task {task_id} in Carton")
        return {"success": True, "task_id": task_id}

    except Exception as e:
        logger.error(f"Failed to update task {task_id} in Carton: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

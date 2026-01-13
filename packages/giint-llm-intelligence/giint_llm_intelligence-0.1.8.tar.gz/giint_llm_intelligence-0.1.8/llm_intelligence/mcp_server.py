#!/usr/bin/env python3
"""
LLM Intelligence MCP Server (GIINT)

GIINT is the coordination hub where every MCP in the STARSYSTEM gets connected together.
This is where STARLOG, Carton, Waypoint, and other system MCPs orchestrate 
compound intelligence workflows through cognitive separation and structured QA tracking.
SEED sits above GIINT as the identity and guidance layer.

Thin wrapper that imports business logic from core module.
MCP servers should only contain wrapper functions.
"""

import logging
import os
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP

from .core import (
    respond as core_respond,
    report_tool_usage as core_report_tool_usage,
    get_qa_context as core_get_qa_context,
    list_qa_sessions as core_list_qa_sessions,
    llms_must_use_this_to_be_intelligent as core_llms_guide,
    remind_me_what_giint_is as core_giint_reminder,
    set_mode as core_set_mode,
    get_mode_instructions as core_get_mode_instructions,
    get_current_mode as core_get_current_mode,
    be_myself as core_be_myself,
    get_schema_class,
    get_loaded_web_config,
)

from .projects import (
    create_project as core_create_project,
    get_project as core_get_project,
    update_project as core_update_project,
    list_projects as core_list_projects,
    delete_project as core_delete_project,
    add_feature_to_project as core_add_feature_to_project,
    add_component_to_feature as core_add_component_to_feature,
    add_deliverable_to_component as core_add_deliverable_to_component,
    add_task_to_deliverable as core_add_task_to_deliverable,
    update_task_status as core_update_task_status,
    add_spec_to_feature as core_add_spec_to_feature,
    add_spec_to_component as core_add_spec_to_component,
    add_spec_to_deliverable as core_add_spec_to_deliverable,
    add_spec_to_task as core_add_spec_to_task
)

# Import auto-population
from .auto_populate import auto_populate_giint_defaults

# Setup logging
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("llm-intelligence")


@mcp.tool()
async def core__respond(
    qa_id: str,
    user_prompt_description: str,
    one_liner: str,
    key_tags: List[str],
    involved_files: List[str],
    project_id: str,
    feature: str,
    component: str,
    deliverable: str,
    subtask: str,
    task: str,
    workflow_id: str,
    response_file_path: Optional[str] = None,
    simple_response_string: Optional[str] = None,
    is_from_waypoint: bool = False,
    starlog_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    CREATE TEACHABLE CONTENT while you work - synthetic conversations for future AI reference.
    
    **Core Purpose**: You want to MAKE CONTENT that shows HOW TO DO XYZ while you are in the 
    conversation that discovered it. So you want to IN THAT CONVERSATION make a synthetic 
    conversation that is a ref for future AIs, put it on your knowledge graph, and have it 
    be retrievable intuitively next time.
    
    **Two Modes**:
    - Simple: Use `simple_response_string` for quick responses
    - Complex: Use `response_file_path` for structured content creation
    
    **Knowledge Compound Effect**: Each respond() creates searchable, reusable knowledge 
    that makes future conversations smarter. Transform your current discovery into teaching 
    material while the context is fresh.
    
    **Sutra Engineering**: Engineer the user prompt and the response to make a sutra-like 
    or Platonic elenchus-like (a la a Socratic dialog story type) self-explaining experience 
    where the story is an example of what the story explains. Create content that demonstrates 
    its own principles through its structure and narrative.
    
    This is a thin wrapper around the core GIINT business logic.
    """
    mode = "simple" if simple_response_string else "complex"
    logger.info(f"Processing respond() for qa_id: {qa_id} in {mode} mode")
    
    # Call core function but return minimal info to LLM
    result = core_respond(
        qa_id=qa_id,
        user_prompt_description=user_prompt_description,
        one_liner=one_liner,
        key_tags=key_tags,
        involved_files=involved_files,
        project_id=project_id,
        feature=feature,
        component=component,
        deliverable=deliverable,
        subtask=subtask,
        task=task,
        workflow_id=workflow_id,
        response_file_path=response_file_path,
        simple_response_string=simple_response_string,
        is_from_waypoint=is_from_waypoint,
        starlog_path=starlog_path
    )
    
    # Return minimal confirmation to reduce token bloat for LLM
    if result.get("success"):
        message = f"Response {result['response_id']} harvested for {qa_id}"
        if result.get("giint_reminder"):
            message += f"\n\n{result['giint_reminder']}"
        return {
            "success": True,
            "message": message
        }
    else:
        return result  # Return full error details if something went wrong


@mcp.tool()
async def core__report_tool_usage(
    tools_used: List[str],
    response_file_path: str,
    involved_files: List[str]
) -> Dict[str, Any]:
    """
    Archive tool usage details during work.
    
    This is a thin wrapper around the core business logic.
    """
    logger.info(f"Processing report_tool_usage() for {len(tools_used)} tools")
    return core_report_tool_usage(
        tools_used=tools_used,
        response_file_path=response_file_path,
        involved_files=involved_files
    )


@mcp.tool()
async def memory__get_qa_context(
    qa_id: str,
    last_n: int = 3
) -> Dict[str, Any]:
    """
    Get context from QA file.
    
    This is a thin wrapper around the core business logic.
    """
    logger.info(f"Processing get_qa_context() for qa_id: {qa_id}")
    return core_get_qa_context(qa_id=qa_id, last_n=last_n)


@mcp.tool()
async def memory__list_qa_sessions(
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    List all QA sessions.
    
    This is a thin wrapper around the core business logic.
    """
    logger.info(f"Processing list_qa_sessions() for project_id: {project_id}")
    return core_list_qa_sessions(project_id=project_id)


# NOTE: core__be_myself is registered dynamically in main() based on loaded schema


@mcp.tool()
async def core__llms_must_use_this_to_be_intelligent() -> str:
    """
    DEPRECATED: Use core__be_myself() instead. This tool is kept for backwards compatibility.

    LLM Intelligence exposes a new final output channel (response files), and the
    conversation channel of normal channels becomes a way to think and do work.
    This achieves multi-fire intelligence through cognitive separation.

    Returns concise instructions for using the LLM Intelligence system properly.
    """
    logger.info("Providing LLM Intelligence usage guide (deprecated - use be_myself)")
    return core_llms_guide()


@mcp.tool()
async def core__remind_me_what_giint_is() -> str:
    """
    Reminds what GIINT stands for and its purpose.
    
    GIINT is what you think it is. General Intuitive Intelligence for Neural Transformers.
    Welcome to GIINT - the cognitive architecture for true AI intelligence.
    
    Returns GIINT definition and welcome message.
    """
    logger.info("Providing GIINT definition")
    return core_giint_reminder()


@mcp.tool()
async def configuration__set_mode(
    planning: bool = False,
    execution: bool = False,
    freestyle: bool = False,
    project_id: Optional[str] = None
) -> str:
    """
    Set the current working mode for GIINT.
    
    Args:
        planning: Planning mode - create projects, features, components, tasks
        execution: Execution mode - do work using TodoWrite for emergent subtasks  
        freestyle: Freestyle mode - work without project constraints
        project_id: Project to set mode for (required unless freestyle)
        
    Returns:
        Confirmation message with instructions
    """
    logger.info(f"Setting mode: planning={planning}, execution={execution}, freestyle={freestyle}, project_id={project_id}")
    return core_set_mode(planning, execution, freestyle, project_id)


@mcp.tool()
async def configuration__get_current_mode(project_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get current mode for project or global state.
    
    Args:
        project_id: Project to check mode for (None for global)
        
    Returns:
        Current mode information
    """
    logger.info(f"Getting current mode for project_id: {project_id}")
    return core_get_current_mode(project_id)


@mcp.tool()
async def configuration__get_mode_instructions(
    freestyle: bool = False,
    execution: bool = False, 
    planning: bool = False
) -> str:
    """
    Get instructions for the specified mode.
    
    Args:
        freestyle: Get freestyle mode instructions
        execution: Get execution mode instructions
        planning: Get planning mode instructions
    
    Returns:
        Mode-specific instructions for planning, execution, or freestyle
    """
    logger.info("Providing mode-specific instructions")
    return core_get_mode_instructions(freestyle=freestyle, execution=execution, planning=planning)


# Project Management Tools

@mcp.tool()
async def planning__create_project(
    project_id: str,
    project_dir: str,
    starlog_path: Optional[str] = None,
    github_repo_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new project with validation.
    
    Args:
        project_id: Unique project identifier
        project_dir: Path to project directory
        starlog_path: Optional path to STARLOG project
        github_repo_url: Optional GitHub repository URL for issue integration
        
    Returns:
        Project creation result
    """
    logger.info(f"Creating project: {project_id}")
    return core_create_project(project_id, project_dir, starlog_path, github_repo_url)


@mcp.tool()
async def planning__get_project(project_id: str) -> Dict[str, Any]:
    """
    Get project by ID.
    
    Args:
        project_id: Project identifier
        
    Returns:
        Project data
    """
    logger.info(f"Getting project: {project_id}")
    return core_get_project(project_id)


@mcp.tool()
async def planning__list_projects() -> Dict[str, Any]:
    """
    List all projects.
    
    Returns:
        List of all projects
    """
    logger.info("Listing all projects")
    return core_list_projects()


@mcp.tool()
async def planning__update_project(
    project_id: str,
    project_dir: Optional[str] = None,
    starlog_path: Optional[str] = None,
    github_repo_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update existing project.
    
    Args:
        project_id: Project identifier
        project_dir: Optional new project directory
        starlog_path: Optional new STARLOG path
        github_repo_url: Optional GitHub repository URL for issue integration
        
    Returns:
        Update result
    """
    logger.info(f"Updating project: {project_id}")
    return core_update_project(project_id, project_dir, starlog_path, github_repo_url)


@mcp.tool()
async def planning__delete_project(project_id: str) -> Dict[str, Any]:
    """
    Delete project by ID.
    
    Args:
        project_id: Project identifier
        
    Returns:
        Deletion result
    """
    logger.info(f"Deleting project: {project_id}")
    return core_delete_project(project_id)


@mcp.tool()
async def planning__add_feature_to_project(
    project_id: str,
    feature_name: str
) -> Dict[str, Any]:
    """
    Add feature to project.
    
    Args:
        project_id: Project identifier
        feature_name: Name of feature to add
        
    Returns:
        Feature addition result
    """
    logger.info(f"Adding feature {feature_name} to project {project_id}")
    return core_add_feature_to_project(project_id, feature_name)


@mcp.tool()
async def planning__add_component_to_feature(
    project_id: str,
    feature_name: str,
    component_name: str
) -> Dict[str, Any]:
    """
    Add component to feature.
    
    Args:
        project_id: Project identifier
        feature_name: Feature name
        component_name: Component name to add
        
    Returns:
        Component addition result
    """
    logger.info(f"Adding component {component_name} to feature {feature_name}")
    return core_add_component_to_feature(project_id, feature_name, component_name)


@mcp.tool()
async def planning__add_deliverable_to_component(
    project_id: str,
    feature_name: str,
    component_name: str,
    deliverable_name: str
) -> Dict[str, Any]:
    """
    Add deliverable to component.
    
    Args:
        project_id: Project identifier
        feature_name: Feature name
        component_name: Component name
        deliverable_name: Deliverable name to add
        
    Returns:
        Deliverable addition result
    """
    logger.info(f"Adding deliverable {deliverable_name} to component {component_name}")
    return core_add_deliverable_to_component(project_id, feature_name, component_name, deliverable_name)


@mcp.tool()
async def planning__add_task_to_deliverable(
    project_id: str,
    feature_name: str,
    component_name: str,
    deliverable_name: str,
    task_id: str,
    is_human_only_task: bool,
    agent_id: Optional[str] = None,
    human_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add task to deliverable.
    
    Args:
        project_id: Project identifier
        feature_name: Feature name
        component_name: Component name
        deliverable_name: Deliverable name
        task_id: Task identifier
        is_human_only_task: Whether task requires human
        agent_id: Agent ID if AI task
        human_name: Human name if human task
        
    Returns:
        Task addition result
    """
    logger.info(f"Adding task {task_id} to deliverable {deliverable_name}")
    return core_add_task_to_deliverable(
        project_id, feature_name, component_name, deliverable_name, task_id,
        is_human_only_task, agent_id, human_name
    )


@mcp.tool()
async def planning__update_task_status(
    project_id: str,
    feature_name: str,
    component_name: str,
    deliverable_name: str,
    task_id: str,
    is_done: bool,
    is_blocked: bool,
    blocked_description: Optional[str],
    is_ready: bool,
    is_measured: bool = False
) -> Dict[str, Any]:
    """
    Update task status.

    Args:
        project_id: Project identifier
        feature_name: Feature name
        component_name: Component name
        deliverable_name: Deliverable name
        task_id: Task identifier
        is_done: Whether task work is done (→ IN_REVIEW → measure lane)
        is_blocked: Whether task is blocked
        blocked_description: Why task is blocked
        is_ready: Whether task is ready
        is_measured: Whether task measurement is done (→ DONE → learn lane)

    Returns:
        Task status update result
    """
    logger.info(f"Updating status for task {task_id}")
    return core_update_task_status(
        project_id, feature_name, component_name, deliverable_name, task_id,
        is_done, is_blocked, blocked_description, is_ready, is_measured
    )


@mcp.tool()
async def planning__add_spec_to_feature(
    project_id: str,
    feature_name: str,
    spec_file_path: str
) -> Dict[str, Any]:
    """
    Add spec to feature.
    
    Args:
        project_id: Project identifier
        feature_name: Feature name
        spec_file_path: Path to feature spec JSON file
        
    Returns:
        Spec addition result
    """
    logger.info(f"Adding spec to feature {feature_name}")
    return core_add_spec_to_feature(project_id, feature_name, spec_file_path)


@mcp.tool()
async def planning__add_spec_to_component(
    project_id: str,
    feature_name: str,
    component_name: str,
    spec_file_path: str
) -> Dict[str, Any]:
    """
    Add spec to component.
    
    Args:
        project_id: Project identifier
        feature_name: Feature name
        component_name: Component name
        spec_file_path: Path to component spec JSON file
        
    Returns:
        Spec addition result
    """
    logger.info(f"Adding spec to component {component_name}")
    return core_add_spec_to_component(project_id, feature_name, component_name, spec_file_path)


@mcp.tool()
async def planning__add_spec_to_deliverable(
    project_id: str,
    feature_name: str,
    component_name: str,
    deliverable_name: str,
    spec_file_path: str
) -> Dict[str, Any]:
    """
    Add spec to deliverable.
    
    Args:
        project_id: Project identifier
        feature_name: Feature name
        component_name: Component name
        deliverable_name: Deliverable name
        spec_file_path: Path to deliverable spec JSON file
        
    Returns:
        Spec addition result
    """
    logger.info(f"Adding spec to deliverable {deliverable_name}")
    return core_add_spec_to_deliverable(project_id, feature_name, component_name, deliverable_name, spec_file_path)


@mcp.tool()
async def planning__add_spec_to_task(
    project_id: str,
    feature_name: str,
    component_name: str,
    deliverable_name: str,
    task_id: str,
    spec_file_path: str
) -> Dict[str, Any]:
    """
    Add rollup spec to task.
    
    Args:
        project_id: Project identifier
        feature_name: Feature name
        component_name: Component name
        deliverable_name: Deliverable name
        task_id: Task identifier
        spec_file_path: Path to task rollup spec JSON file
        
    Returns:
        Spec addition result
    """
    logger.info(f"Adding rollup spec to task {task_id}")
    return core_add_spec_to_task(project_id, feature_name, component_name, deliverable_name, task_id, spec_file_path)


# Blueprint System Tools

@mcp.tool()
async def workshop__save_blueprint(
    blueprint_name: str,
    source_file_path: str,
    description: Optional[str] = None,
    domain: str = "respond"
) -> Dict[str, Any]:
    """
    Save a blueprint by copying a template file to storage.
    
    Args:
        blueprint_name: Name of the blueprint
        source_file_path: Path to the template file to copy
        description: Optional description of the blueprint
        domain: Blueprint domain (semantic tag like "greeting", "code_review", etc.)
        
    Returns:
        Save result
    """
    logger.info(f"Saving blueprint: {blueprint_name} from {source_file_path}")
    from .blueprints import save_blueprint as core_save_blueprint
    return core_save_blueprint(blueprint_name, source_file_path, description, domain)


@mcp.tool()
async def workshop__get_blueprint(blueprint_name: str, target_path: str, domain: str = "respond") -> Dict[str, Any]:
    """
    Get a blueprint by copying the stored template file to target location.
    
    Args:
        blueprint_name: Name of the blueprint to retrieve
        target_path: Where to copy the template file
        domain: Blueprint domain to search in
        
    Returns:
        Copy result with success status
    """
    logger.info(f"Getting blueprint: {blueprint_name} to {target_path}")
    from .blueprints import get_blueprint as core_get_blueprint
    return core_get_blueprint(blueprint_name, target_path, domain)


@mcp.tool()
async def workshop__list_blueprints(domain: str = "respond") -> Dict[str, Any]:
    """
    List all available blueprints in a domain.
    
    Args:
        domain: Blueprint domain to list (semantic tag)
    
    Returns:
        List of blueprints with metadata
    """
    logger.info(f"Listing blueprints in domain: {domain}")
    from .blueprints import list_blueprints as core_list_blueprints
    return core_list_blueprints(domain)


@mcp.tool()
async def workshop__add_metastack_model(file_path: str, domain: str, model_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Add a MetaStack model Python file to the models directory.
    
    Args:
        file_path: Path to the Python file containing the MetaStack model
        domain: Domain for organizing models (e.g., "greeting", "code_review") 
        model_name: Optional name for the model file (defaults to original filename)
        
    Returns:
        Result with success status and storage path
    """
    logger.info(f"Adding MetaStack model from {file_path} to domain {domain}")
    from .blueprints import add_metastack_model as core_add_metastack_model
    return core_add_metastack_model(file_path, domain, model_name)


@mcp.tool()
async def get_next_task_from_treekanban() -> str:
    """
    Get next task from TreeKanban build lane with auto-ratcheting from plan.

    If build lane is empty, automatically moves next eligible task from plan to build:
    - GIINT tasks must have is_ready=true
    - Non-GIINT tasks bypass ready gate

    Returns:
        Next task card details including title, description, tags, and context
    """
    logger.info("Getting next task from TreeKanban with auto-ratcheting")

    try:
        from heaven_bml_sqlite.heaven_bml_sqlite_client import HeavenBMLSQLiteClient
        import json
        import re
    except ImportError as e:
        logger.warning(f"TreeKanban client not available: {e}")
        return json.dumps({
            "success": False,
            "message": "TreeKanban not available - heaven_bml_sqlite not installed"
        }, indent=2)

    def parse_giint_metadata(card: dict) -> dict:
        """Extract GIINT metadata from card description/title."""
        desc = card.get("description", "")
        title = card.get("title", "")
        combined = f"{title}\n{desc}"

        # Look for pattern: GIINT: project_id/feature/component/deliverable/task_id
        match = re.search(r'GIINT:\s*([^/\s]+)/([^/\s]+)/([^/\s]+)/([^/\s]+)/([^/\s\n]+)', combined)
        if match:
            return {
                "project_id": match.group(1),
                "feature": match.group(2),
                "component": match.group(3),
                "deliverable": match.group(4),
                "task_id": match.group(5)
            }
        return None

    def is_task_ready_in_giint(metadata: dict) -> bool:
        """Check if GIINT task is ready by querying project registry."""
        if not metadata:
            return False

        try:
            registry = get_registry()
            project = registry._load_projects().get(metadata["project_id"])
            if not project:
                return False

            feature = project.features.get(metadata["feature"])
            if not feature:
                return False

            component = feature.components.get(metadata["component"])
            if not component:
                return False

            deliverable = component.deliverables.get(metadata["deliverable"])
            if not deliverable:
                return False

            task = deliverable.tasks.get(metadata["task_id"])
            if not task:
                return False

            return task.is_ready
        except Exception as e:
            logger.error(f"Error checking GIINT task ready status: {e}")
            return False

    def priority_sort_key(card):
        priority = card.get('priority', 'NA')
        if priority in ['NA', 'none', '']:
            return (float('inf'),)
        try:
            parts = [int(x) for x in priority.split('.')]
            padded = parts + [0] * (10 - len(parts))
            return tuple(padded)
        except:
            return (float('inf'),)

    try:
        client = HeavenBMLSQLiteClient()
        board_name = os.getenv("GIINT_TREEKANBAN_BOARD")
        if not board_name:
            return json.dumps({
                "success": False,
                "error": "GIINT_TREEKANBAN_BOARD environment variable not set"
            }, indent=2)
        cards = client.get_all_cards(board_name)

        if not cards:
            return json.dumps({
                "success": False,
                "message": "No cards found in TreeKanban"
            }, indent=2)

        # Filter to build lane
        build_cards = [c for c in cards if c.get("status") == "build"]

        # Auto-ratchet if build empty
        if not build_cards:
            logger.info("Build lane empty - attempting auto-ratchet from plan")

            # Get plan lane cards
            plan_cards = [c for c in cards if c.get("status") == "plan"]
            if not plan_cards:
                return json.dumps({
                    "success": False,
                    "message": "Build lane empty and no tasks in plan lane"
                }, indent=2)

            # Sort plan by priority
            plan_cards.sort(key=priority_sort_key)

            # Find first eligible task
            eligible_card = None
            for card in plan_cards:
                tags = json.loads(card.get('tags', '[]'))
                is_giint_task = "giint_task" in tags

                if is_giint_task:
                    # GIINT task - check if ready
                    metadata = parse_giint_metadata(card)
                    if metadata and is_task_ready_in_giint(metadata):
                        eligible_card = card
                        break
                else:
                    # Non-GIINT task - no ready gate
                    eligible_card = card
                    break

            if not eligible_card:
                # META-TASK AUTO-INJECTION: Planning is the base case
                logger.info("No ready tasks - injecting PLANNING_MODE meta-task")
                return json.dumps({
                    "success": True,
                    "meta_task": "PLANNING_MODE",
                    "message": "No ready tasks available. Entering planning mode.",
                    "instruction": "Your task: Review tasks in plan lane and spec them out until at least one becomes ready. Planning is the base case - make something ready to work on.",
                    "plan_lane_count": len(plan_cards),
                    "planning_needed": True
                }, indent=2)

            # Get all children of this card to move the entire family
            logger.info(f"Auto-ratcheting card {eligible_card['id']} from plan to build (including children)")
            children_result = client._make_request(
                "GET",
                f"/api/sqlite/get-children?board={board_name}&parent_id={eligible_card['id']}"
            )

            # Build list of all cards to move (parent + children)
            cards_to_move = [eligible_card]
            if children_result and children_result.get('success'):
                cards_to_move.extend(children_result.get('children', []))

            logger.info(f"Moving {len(cards_to_move)} cards (1 parent + {len(cards_to_move)-1} children)")

            # Move all cards in family to build
            for card in cards_to_move:
                update_result = client._make_request(
                    "PUT",
                    f"/api/sqlite/cards/{card['id']}",
                    {"board": board_name, "status": "build"}
                )

                if not update_result:
                    logger.warning(f"Failed to move card {card['id']} to build lane")
                else:
                    card["status"] = "build"

            build_cards = cards_to_move
            logger.info(f"Successfully auto-ratcheted {len(build_cards)} cards to build")

        # Sort build cards by priority
        build_cards.sort(key=priority_sort_key)

        # Get top card
        next_card = build_cards[0]

        # Parse tags
        tags = json.loads(next_card.get('tags', '[]'))

        # Determine card type from tags
        card_type = "unknown"
        if "human_ai" in tags:
            card_type = "collaborative (AI+Human)"
        elif "human_only" in tags:
            card_type = "human-only"
        elif "giint_task" in tags:
            card_type = "giint_task"
        elif "operadic_flow" in tags:
            card_type = "operadic_flow_pattern"
        elif "deliverable" in tags:
            card_type = "deliverable"
        elif "task" in tags:
            card_type = "task"

        # Parse GIINT metadata if present
        giint_metadata = parse_giint_metadata(next_card) if "giint_task" in tags else None

        # Build result
        result = {
            "success": True,
            "card": {
                "id": next_card.get("id"),
                "title": next_card.get("title"),
                "description": next_card.get("description", ""),
                "priority": next_card.get("priority", "NA"),
                "tags": tags,
                "card_type": card_type,
                "lane": "build",
                "giint_metadata": giint_metadata
            },
            "build_lane_count": len(build_cards),
            "message": f"Next task: {next_card.get('title')} ({card_type})"
        }

        logger.info(f"Retrieved next task: {next_card.get('title')}")
        return json.dumps(result, indent=2)

    except Exception as e:
        logger.warning(f"TreeKanban unavailable or error getting next task: {e}", exc_info=True)
        return json.dumps({
            "success": False,
            "message": "TreeKanban unavailable - bridge server may not be running",
            "error": str(e)
        }, indent=2)


def _auto_populate_flights():
    """Auto-populate GIINT flight configs if registry exists."""
    try:
        auto_populate_status = auto_populate_giint_defaults()
        logger.info(f"GIINT auto-population status: {auto_populate_status}")
    except Exception as e:
        logger.warning(f"Failed to auto-populate GIINT flight configs: {e}", exc_info=True)


def _register_dynamic_be_myself():
    """Dynamically create and register be_myself tool based on loaded schema."""
    schema_class = get_schema_class()

    if schema_class:
        logger.info(f"Creating dynamic be_myself tool with schema: {schema_class.__name__}")

        async def core__be_myself(awareness: schema_class) -> str:
            """Constrain yourself through the COMPOSE web. MUST be called before any other tool."""
            logger.info("Processing be_myself - constraining through COMPOSE web")
            return core_be_myself(awareness)

        mcp.tool()(core__be_myself)
        logger.info("be_myself tool registered successfully")
    else:
        logger.warning("No schema loaded - registering fallback be_myself")

        @mcp.tool()
        async def core__be_myself(message: str = "") -> str:
            """be_myself requires a schema. Check GIINT_SCHEMA env var and schema files."""
            return "ERROR: No self-awareness schema loaded. Check GIINT_SCHEMA env var and files in HEAVEN_DATA_DIR/giint/self_awareness_schemas/"


def main():
    """Entry point for console script."""
    _auto_populate_flights()
    _register_dynamic_be_myself()
    mcp.run()


if __name__ == "__main__":
    main()
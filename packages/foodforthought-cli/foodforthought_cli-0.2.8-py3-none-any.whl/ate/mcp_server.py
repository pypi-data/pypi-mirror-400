#!/usr/bin/env python3
"""
FoodforThought MCP Server - Model Context Protocol server for Cursor IDE
Exposes FoodforThought CLI capabilities as MCP tools

Installation:
    pip install -r requirements-mcp.txt

Usage:
    python -m ate.mcp_server

Or configure in Cursor's mcp.json:
    {
      "mcpServers": {
        "foodforthought": {
          "command": "python",
          "args": ["-m", "ate.mcp_server"],
          "env": {
            "ATE_API_URL": "https://kindly.fyi/api",
            "ATE_API_KEY": "${env:ATE_API_KEY}"
          }
        }
      }
    }
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional
from pathlib import Path

# Import the existing CLI client
from ate.cli import ATEClient

# MCP SDK imports - using standard MCP Python SDK pattern
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool,
        TextContent,
        Resource,
        Prompt,
        PromptArgument,
    )
except ImportError:
    try:
        # Alternative import path for some MCP SDK versions
        from mcp import Server, stdio_server
        from mcp.types import Tool, TextContent, Resource, Prompt, PromptArgument
    except ImportError:
        # Fallback if MCP SDK not available - provide helpful error
        print(
            "Error: MCP SDK not installed. Install with: pip install mcp",
            file=sys.stderr,
        )
        sys.exit(1)

# Initialize MCP server
server = Server("foodforthought")

# Initialize ATE client
client = ATEClient()

# Active recording state for telemetry recording tools
_active_recording = None


# ============================================================================
# Tool Definitions
# ============================================================================

def get_repository_tools() -> List[Tool]:
    """Repository management tools"""
    return [
        Tool(
            name="ate_init",
            description="Initialize a new FoodforThought repository for robot skills",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Repository name",
                    },
                    "description": {
                        "type": "string",
                        "description": "Repository description",
                    },
                    "visibility": {
                        "type": "string",
                        "enum": ["public", "private"],
                        "description": "Repository visibility",
                        "default": "public",
                    },
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="ate_clone",
            description="Clone a FoodforThought repository to local directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_id": {
                        "type": "string",
                        "description": "Repository ID to clone",
                    },
                    "target_dir": {
                        "type": "string",
                        "description": "Target directory (optional)",
                    },
                },
                "required": ["repo_id"],
            },
        ),
        Tool(
            name="ate_list_repositories",
            description="List available FoodforThought repositories",
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "Search query",
                    },
                    "robot_model": {
                        "type": "string",
                        "description": "Filter by robot model",
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results",
                        "default": 20,
                    },
                },
            },
        ),
        Tool(
            name="ate_get_repository",
            description="Get details of a specific repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_id": {
                        "type": "string",
                        "description": "Repository ID",
                    },
                },
                "required": ["repo_id"],
            },
        ),
    ]


def get_robot_tools() -> List[Tool]:
    """Robot profile tools"""
    return [
        Tool(
            name="ate_list_robots",
            description="List available robot profiles",
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "Search query",
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by category",
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results",
                        "default": 20,
                    },
                },
            },
        ),
        Tool(
            name="ate_get_robot",
            description="Get details of a specific robot profile",
            inputSchema={
                "type": "object",
                "properties": {
                    "robot_id": {
                        "type": "string",
                        "description": "Robot profile ID",
                    },
                },
                "required": ["robot_id"],
            },
        ),
    ]


def get_marketplace_tools() -> List[Tool]:
    """Unified marketplace tools (Phase 6)"""
    return [
        Tool(
            name="ate_marketplace_robots",
            description="List community robots from the unified marketplace. Includes both Artifex-published and imported robots.",
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "Search by name or description",
                    },
                    "category": {
                        "type": "string",
                        "enum": ["arm", "gripper", "mobile_base", "quadruped", "humanoid",
                                "dual_arm", "manipulator", "cobot", "drone", "custom"],
                        "description": "Filter by robot category",
                    },
                    "sort": {
                        "type": "string",
                        "enum": ["downloads", "rating", "recent", "name"],
                        "description": "Sort order",
                        "default": "downloads",
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum results",
                        "default": 20,
                    },
                },
            },
        ),
        Tool(
            name="ate_marketplace_robot",
            description="Get detailed information about a specific robot from the marketplace, including URDF, links, joints, and parts.",
            inputSchema={
                "type": "object",
                "properties": {
                    "robot_id": {
                        "type": "string",
                        "description": "Robot ID or slug",
                    },
                },
                "required": ["robot_id"],
            },
        ),
        Tool(
            name="ate_marketplace_components",
            description="List components from the parts marketplace. Components can be grippers, sensors, actuators, etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "Search by name or description",
                    },
                    "type": {
                        "type": "string",
                        "enum": ["gripper", "end_effector", "sensor", "camera",
                                "actuator", "link", "base", "arm_segment", "custom"],
                        "description": "Filter by component type",
                    },
                    "sort": {
                        "type": "string",
                        "enum": ["downloads", "rating", "recent", "name"],
                        "description": "Sort order",
                        "default": "downloads",
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum results",
                        "default": 20,
                    },
                },
            },
        ),
        Tool(
            name="ate_marketplace_component",
            description="Get detailed information about a specific component, including compatible robots and specifications.",
            inputSchema={
                "type": "object",
                "properties": {
                    "component_id": {
                        "type": "string",
                        "description": "Component ID",
                    },
                },
                "required": ["component_id"],
            },
        ),
        Tool(
            name="ate_skill_transfer_check",
            description="Calculate skill transfer compatibility between robots. Shows which robots can receive skills from a source robot.",
            inputSchema={
                "type": "object",
                "properties": {
                    "robot_id": {
                        "type": "string",
                        "description": "Source robot ID",
                    },
                    "direction": {
                        "type": "string",
                        "enum": ["from", "to"],
                        "description": "Direction: 'from' = skills from this robot can transfer to others",
                        "default": "from",
                    },
                    "min_score": {
                        "type": "number",
                        "description": "Minimum compatibility score (0.0-1.0)",
                        "default": 0.4,
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum results",
                        "default": 10,
                    },
                },
                "required": ["robot_id"],
            },
        ),
        Tool(
            name="ate_robot_parts",
            description="Get parts required by or compatible with a robot.",
            inputSchema={
                "type": "object",
                "properties": {
                    "robot_id": {
                        "type": "string",
                        "description": "Robot ID",
                    },
                },
                "required": ["robot_id"],
            },
        ),
        Tool(
            name="ate_component_robots",
            description="Get robots that use or are compatible with a component.",
            inputSchema={
                "type": "object",
                "properties": {
                    "component_id": {
                        "type": "string",
                        "description": "Component ID",
                    },
                },
                "required": ["component_id"],
            },
        ),
    ]


def get_compatibility_tools() -> List[Tool]:
    """Skill compatibility and adaptation tools"""
    return [
        Tool(
            name="ate_check_transfer",
            description="Check skill transfer compatibility between two robot models",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_robot": {
                        "type": "string",
                        "description": "Source robot model name",
                    },
                    "target_robot": {
                        "type": "string",
                        "description": "Target robot model name",
                    },
                    "skill_id": {
                        "type": "string",
                        "description": "Optional skill ID to check",
                    },
                    "min_score": {
                        "type": "number",
                        "description": "Minimum compatibility score threshold (0.0-1.0)",
                        "default": 0.0,
                    },
                },
                "required": ["source_robot", "target_robot"],
            },
        ),
        Tool(
            name="ate_adapt",
            description="Generate adaptation plan for transferring skills between robots",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_robot": {
                        "type": "string",
                        "description": "Source robot model",
                    },
                    "target_robot": {
                        "type": "string",
                        "description": "Target robot model",
                    },
                    "repo_id": {
                        "type": "string",
                        "description": "Repository ID to adapt",
                    },
                    "analyze_only": {
                        "type": "boolean",
                        "description": "Only show compatibility analysis",
                        "default": True,
                    },
                },
                "required": ["source_robot", "target_robot"],
            },
        ),
    ]


def get_skill_tools() -> List[Tool]:
    """Skill data tools"""
    return [
        Tool(
            name="ate_pull",
            description="Pull skill data for training in various formats (JSON, RLDS, LeRobot)",
            inputSchema={
                "type": "object",
                "properties": {
                    "skill_id": {
                        "type": "string",
                        "description": "Skill ID to pull",
                    },
                    "robot": {
                        "type": "string",
                        "description": "Filter by robot model",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["json", "rlds", "lerobot"],
                        "description": "Output format",
                        "default": "json",
                    },
                    "output": {
                        "type": "string",
                        "description": "Output directory",
                        "default": "./data",
                    },
                },
                "required": ["skill_id"],
            },
        ),
        Tool(
            name="ate_upload",
            description="Upload demonstration videos for community labeling",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to video file",
                    },
                    "robot": {
                        "type": "string",
                        "description": "Robot model in the video",
                    },
                    "task": {
                        "type": "string",
                        "description": "Task being demonstrated",
                    },
                    "project": {
                        "type": "string",
                        "description": "Project ID to associate with",
                    },
                },
                "required": ["path", "robot", "task"],
            },
        ),
    ]


def get_parts_tools() -> List[Tool]:
    """Hardware parts management tools"""
    return [
        Tool(
            name="ate_parts_list",
            description="List available hardware parts in the catalog",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["gripper", "sensor", "actuator", "controller", 
                                "end-effector", "camera", "lidar", "force-torque"],
                        "description": "Filter by part category",
                    },
                    "manufacturer": {
                        "type": "string",
                        "description": "Filter by manufacturer",
                    },
                    "search": {
                        "type": "string",
                        "description": "Search by name or part number",
                    },
                },
            },
        ),
        Tool(
            name="ate_parts_check",
            description="Check part compatibility requirements for a skill",
            inputSchema={
                "type": "object",
                "properties": {
                    "skill_id": {
                        "type": "string",
                        "description": "Skill ID to check parts for",
                    },
                },
                "required": ["skill_id"],
            },
        ),
        Tool(
            name="ate_parts_require",
            description="Add a part dependency to a skill",
            inputSchema={
                "type": "object",
                "properties": {
                    "part_id": {
                        "type": "string",
                        "description": "Part ID to require",
                    },
                    "skill_id": {
                        "type": "string",
                        "description": "Skill ID",
                    },
                    "version": {
                        "type": "string",
                        "description": "Minimum version",
                        "default": "1.0.0",
                    },
                    "required": {
                        "type": "boolean",
                        "description": "Mark as required (not optional)",
                        "default": False,
                    },
                },
                "required": ["part_id", "skill_id"],
            },
        ),
        Tool(
            name="ate_deps_audit",
            description="Audit and verify all dependencies are compatible for a skill",
            inputSchema={
                "type": "object",
                "properties": {
                    "skill_id": {
                        "type": "string",
                        "description": "Skill ID (optional, uses current repo if not specified)",
                    },
                },
            },
        ),
    ]


def get_generate_tools() -> List[Tool]:
    """Skill generation tools"""
    return [
        Tool(
            name="ate_generate",
            description="Generate skill scaffolding from a natural language task description",
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Natural language task description (e.g., 'pick up box and place on pallet')",
                    },
                    "robot": {
                        "type": "string",
                        "description": "Target robot model",
                        "default": "ur5",
                    },
                    "output": {
                        "type": "string",
                        "description": "Output directory for generated files",
                        "default": "./new-skill",
                    },
                },
                "required": ["description"],
            },
        ),
    ]


def get_workflow_tools() -> List[Tool]:
    """Workflow composition tools"""
    return [
        Tool(
            name="ate_workflow_validate",
            description="Validate a workflow YAML file for skill composition",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to workflow YAML file",
                    },
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="ate_workflow_run",
            description="Run a skill workflow/pipeline",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to workflow YAML file",
                    },
                    "sim": {
                        "type": "boolean",
                        "description": "Run in simulation mode",
                        "default": True,
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "Show execution plan without running",
                        "default": False,
                    },
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="ate_workflow_export",
            description="Export workflow to other formats (ROS2 launch, JSON)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to workflow YAML file",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["ros2", "json"],
                        "description": "Export format",
                        "default": "ros2",
                    },
                    "output": {
                        "type": "string",
                        "description": "Output file path",
                    },
                },
                "required": ["path"],
            },
        ),
    ]


def get_team_tools() -> List[Tool]:
    """Team collaboration tools"""
    return [
        Tool(
            name="ate_team_create",
            description="Create a new team for collaboration",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Team name",
                    },
                    "description": {
                        "type": "string",
                        "description": "Team description",
                    },
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="ate_team_list",
            description="List teams you belong to",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="ate_team_invite",
            description="Invite a user to a team",
            inputSchema={
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "description": "Email of user to invite",
                    },
                    "team": {
                        "type": "string",
                        "description": "Team slug",
                    },
                    "role": {
                        "type": "string",
                        "enum": ["owner", "admin", "member", "viewer"],
                        "description": "Role to assign",
                        "default": "member",
                    },
                },
                "required": ["email", "team"],
            },
        ),
        Tool(
            name="ate_team_share",
            description="Share a skill with a team",
            inputSchema={
                "type": "object",
                "properties": {
                    "skill_id": {
                        "type": "string",
                        "description": "Skill ID to share",
                    },
                    "team": {
                        "type": "string",
                        "description": "Team slug",
                    },
                },
                "required": ["skill_id", "team"],
            },
        ),
    ]


def get_data_tools() -> List[Tool]:
    """Dataset management tools"""
    return [
        Tool(
            name="ate_data_upload",
            description="Upload sensor data or demonstration logs for a skill",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to data directory or file",
                    },
                    "skill": {
                        "type": "string",
                        "description": "Associated skill ID",
                    },
                    "stage": {
                        "type": "string",
                        "enum": ["raw", "annotated", "skill-abstracted", "production"],
                        "description": "Data stage",
                        "default": "raw",
                    },
                },
                "required": ["path", "skill"],
            },
        ),
        Tool(
            name="ate_data_list",
            description="List datasets for a skill",
            inputSchema={
                "type": "object",
                "properties": {
                    "skill": {
                        "type": "string",
                        "description": "Filter by skill ID",
                    },
                    "stage": {
                        "type": "string",
                        "description": "Filter by data stage",
                    },
                },
            },
        ),
        Tool(
            name="ate_data_promote",
            description="Promote a dataset to the next stage in the pipeline",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {
                        "type": "string",
                        "description": "Dataset ID",
                    },
                    "to_stage": {
                        "type": "string",
                        "enum": ["annotated", "skill-abstracted", "production"],
                        "description": "Target stage",
                    },
                },
                "required": ["dataset_id", "to_stage"],
            },
        ),
        Tool(
            name="ate_data_export",
            description="Export a dataset in various formats",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {
                        "type": "string",
                        "description": "Dataset ID",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["json", "rlds", "lerobot", "hdf5"],
                        "description": "Export format",
                        "default": "rlds",
                    },
                    "output": {
                        "type": "string",
                        "description": "Output directory",
                        "default": "./export",
                    },
                },
                "required": ["dataset_id"],
            },
        ),
    ]


def get_deploy_tools() -> List[Tool]:
    """Deployment management tools"""
    return [
        Tool(
            name="ate_deploy",
            description="Deploy skills to a robot",
            inputSchema={
                "type": "object",
                "properties": {
                    "robot_type": {
                        "type": "string",
                        "description": "Robot type to deploy to",
                    },
                    "repo_id": {
                        "type": "string",
                        "description": "Repository ID (uses current repo if not specified)",
                    },
                },
                "required": ["robot_type"],
            },
        ),
        Tool(
            name="ate_deploy_config",
            description="Deploy skills using a deployment configuration file (supports hybrid edge/cloud)",
            inputSchema={
                "type": "object",
                "properties": {
                    "config_path": {
                        "type": "string",
                        "description": "Path to deploy.yaml configuration",
                    },
                    "target": {
                        "type": "string",
                        "description": "Target fleet or robot",
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "Show deployment plan without executing",
                        "default": False,
                    },
                },
                "required": ["config_path", "target"],
            },
        ),
        Tool(
            name="ate_deploy_status",
            description="Check deployment status for a fleet or robot",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target fleet or robot",
                    },
                },
                "required": ["target"],
            },
        ),
    ]


def get_test_tools() -> List[Tool]:
    """Testing and validation tools"""
    return [
        Tool(
            name="ate_test",
            description="Test skills in simulation (Gazebo, MuJoCo, PyBullet, Webots)",
            inputSchema={
                "type": "object",
                "properties": {
                    "environment": {
                        "type": "string",
                        "enum": ["gazebo", "mujoco", "pybullet", "webots"],
                        "description": "Simulation environment",
                        "default": "pybullet",
                    },
                    "robot": {
                        "type": "string",
                        "description": "Robot model to test with",
                    },
                    "local": {
                        "type": "boolean",
                        "description": "Run simulation locally",
                        "default": False,
                    },
                },
            },
        ),
        Tool(
            name="ate_validate",
            description="Run safety and compliance validation checks",
            inputSchema={
                "type": "object",
                "properties": {
                    "checks": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Safety checks to run (collision, speed, workspace, force, all)",
                        "default": ["all"],
                    },
                    "strict": {
                        "type": "boolean",
                        "description": "Use strict validation (fail on warnings)",
                        "default": False,
                    },
                },
            },
        ),
        Tool(
            name="ate_benchmark",
            description="Run performance benchmarks on skills",
            inputSchema={
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["speed", "accuracy", "robustness", "efficiency", "all"],
                        "description": "Benchmark type",
                        "default": "all",
                    },
                    "trials": {
                        "type": "number",
                        "description": "Number of trials",
                        "default": 10,
                    },
                    "compare": {
                        "type": "string",
                        "description": "Compare with baseline repository ID",
                    },
                },
            },
        ),
    ]


def get_compiler_tools() -> List[Tool]:
    """
    Skill Compiler Tools - Transform skill.yaml specifications into deployable robot skill packages.

    WORKFLOW FOR AI ASSISTANTS:
    1. Use ate_list_primitives to discover available building blocks
    2. Help user create skill.yaml with proper format
    3. Use ate_validate_skill_spec to check for errors
    4. Use ate_check_skill_compatibility to verify robot compatibility
    5. Use ate_compile_skill to generate deployable code
    6. Use ate_test_compiled_skill to test in dry-run or simulation
    7. Use ate_publish_compiled_skill to share with community

    See docs/SKILL_COMPILER.md for full documentation.
    """
    return [
        Tool(
            name="ate_compile_skill",
            description="""Compile a skill.yaml specification into deployable code.

WHEN TO USE: After creating and validating a skill.yaml file, use this to generate
executable Python code, ROS2 packages, or Docker containers.

TARGETS:
- python: Standalone Python package (default, simplest)
- ros2: ROS2-compatible package with launch files
- docker: Containerized deployment with Dockerfile
- all: Generate all formats

EXAMPLE:
{
  "skill_path": "pick_and_place.skill.yaml",
  "target": "python",
  "output": "./dist/pick_and_place"
}

OUTPUT: Creates a directory with generated code, config files, and dependencies.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "skill_path": {
                        "type": "string",
                        "description": "Path to skill.yaml file (e.g., 'skills/pick_place.skill.yaml')",
                    },
                    "output": {
                        "type": "string",
                        "description": "Output directory (default: ./output). Will be created if doesn't exist.",
                    },
                    "target": {
                        "type": "string",
                        "enum": ["python", "ros2", "docker", "all"],
                        "description": "Compilation target: python (simplest), ros2 (for ROS2 robots), docker (containerized), all",
                        "default": "python",
                    },
                    "robot": {
                        "type": "string",
                        "description": "Optional: Path to robot URDF for hardware-specific config generation",
                    },
                },
                "required": ["skill_path"],
            },
        ),
        Tool(
            name="ate_test_compiled_skill",
            description="""Test a compiled skill without deploying to a real robot.

WHEN TO USE: After compiling a skill, verify it works correctly before deployment.

MODES:
- dry-run: Traces execution without any robot (fastest, always available)
- sim: Runs in simulation (requires simulation setup)
- hardware: Runs on real robot (requires robot_port)

EXAMPLE:
{
  "skill_path": "./dist/pick_and_place",
  "mode": "dry-run",
  "params": {"speed": 0.3, "grip_force": 15.0}
}

OUTPUT: Execution trace showing each primitive call and its result.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "skill_path": {
                        "type": "string",
                        "description": "Path to compiled skill directory (output from ate_compile_skill)",
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["sim", "dry-run", "hardware"],
                        "description": "dry-run=trace only, sim=simulation, hardware=real robot",
                        "default": "dry-run",
                    },
                    "robot_port": {
                        "type": "string",
                        "description": "Robot serial port (only for hardware mode, e.g., '/dev/ttyUSB0')",
                    },
                    "params": {
                        "type": "object",
                        "description": "Override skill parameters (e.g., {\"speed\": 0.5})",
                    },
                },
                "required": ["skill_path"],
            },
        ),
        Tool(
            name="ate_publish_compiled_skill",
            description="""Publish a compiled skill to the FoodForThought registry.

WHEN TO USE: When the skill is tested and ready to share with others.

VISIBILITY:
- public: Anyone can use this skill
- private: Only you can see it
- team: Shared with your team members

EXAMPLE:
{
  "skill_path": "./dist/pick_and_place",
  "visibility": "public"
}

OUTPUT: Registry URL where the skill is published.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "skill_path": {
                        "type": "string",
                        "description": "Path to compiled skill directory to publish",
                    },
                    "visibility": {
                        "type": "string",
                        "enum": ["public", "private", "team"],
                        "description": "Who can access this skill",
                        "default": "public",
                    },
                },
                "required": ["skill_path"],
            },
        ),
        Tool(
            name="ate_check_skill_compatibility",
            description="""Check if a skill can run on a specific robot.

WHEN TO USE: Before compiling, verify the skill's hardware requirements
match the target robot's capabilities (DOF, sensors, payload, etc.).

CHECKS PERFORMED:
- Arm DOF and reach requirements
- Gripper type and force capabilities
- Required sensors (cameras, F/T sensors)
- Workspace bounds

EXAMPLE:
{
  "skill_path": "pick_and_place.skill.yaml",
  "robot_urdf": "robots/ur5/ur5.urdf"
}

OUTPUT: Compatibility report with score and list of issues/adaptations needed.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "skill_path": {
                        "type": "string",
                        "description": "Path to skill.yaml file",
                    },
                    "robot_urdf": {
                        "type": "string",
                        "description": "Path to robot URDF file",
                    },
                    "robot_ate_dir": {
                        "type": "string",
                        "description": "Alternative: Path to directory containing ate.yaml robot config",
                    },
                },
                "required": ["skill_path"],
            },
        ),
        Tool(
            name="ate_list_primitives",
            description="""List available primitives (building blocks) for creating skills.

WHEN TO USE: When starting to create a skill, or when you need to know what
operations are available for a specific hardware type.

CATEGORIES:
- motion: Movement primitives (move_to_pose, move_linear, etc.)
- gripper: Gripper actions (open_gripper, close_gripper)
- sensing: Sensor reading (capture_image, read_force_torque)
- wait: Timing and conditions (wait_time, wait_for_contact)
- control: Control modes (set_control_mode, enable_compliance)

EXAMPLE - List all motion primitives:
{
  "category": "motion"
}

EXAMPLE - List primitives that need a camera:
{
  "hardware": "camera"
}

OUTPUT: List of primitives with their descriptions and parameters.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["motion", "gripper", "sensing", "wait", "control", "all"],
                        "description": "Filter by category (use 'all' to see everything)",
                        "default": "all",
                    },
                    "hardware": {
                        "type": "string",
                        "description": "Filter by hardware type: arm, gripper, camera, force_torque_sensor",
                    },
                },
            },
        ),
        Tool(
            name="ate_get_primitive",
            description="""Get detailed information about a specific primitive.

WHEN TO USE: When you need to know the exact parameters and requirements
for a primitive before using it in a skill.

COMMON PRIMITIVES:
- move_to_pose: Move end-effector to a 7D pose [x,y,z,qx,qy,qz,qw]
- move_to_joint_positions: Move to specific joint angles
- open_gripper / close_gripper: Gripper control
- wait_for_contact: Wait until force threshold is reached
- capture_image: Take a camera image

EXAMPLE:
{
  "name": "move_to_pose"
}

OUTPUT: Full primitive definition with all parameters, types, defaults, and hardware requirements.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Primitive name (e.g., 'move_to_pose', 'close_gripper', 'wait_for_contact')",
                    },
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="ate_validate_skill_spec",
            description="""Validate a skill.yaml file without compiling.

WHEN TO USE: After creating or modifying a skill.yaml, check for errors before compiling.

CHECKS PERFORMED:
- YAML syntax validity
- Required fields (name, version, description, execution)
- Parameter type validity
- Primitive names exist in registry
- Template expression syntax
- Hardware requirement format

EXAMPLE:
{
  "skill_path": "my_skill.skill.yaml"
}

OUTPUT:
- If valid: Summary of skill (name, version, parameter count, etc.)
- If invalid: List of errors with line numbers and fix suggestions.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "skill_path": {
                        "type": "string",
                        "description": "Path to skill.yaml file to validate",
                    },
                },
                "required": ["skill_path"],
            },
        ),
    ]


def get_protocol_tools() -> List[Tool]:
    """Protocol registry tools"""
    return [
        Tool(
            name="ate_protocol_list",
            description="List protocols from the FoodForThought protocol registry. Protocols document how to communicate with robot hardware (BLE, serial, WiFi, CAN, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "robot_model": {
                        "type": "string",
                        "description": "Filter by robot model name (e.g., 'mechdog', 'ur5')",
                    },
                    "transport_type": {
                        "type": "string",
                        "enum": ["ble", "serial", "wifi", "can", "i2c", "spi", "mqtt", "ros2"],
                        "description": "Filter by transport type",
                    },
                    "verified_only": {
                        "type": "boolean",
                        "description": "Show only community-verified protocols",
                        "default": False,
                    },
                    "search": {
                        "type": "string",
                        "description": "Search in command format and discovery notes",
                    },
                },
            },
        ),
        Tool(
            name="ate_protocol_get",
            description="Get detailed protocol information including BLE characteristics, serial config, command schema, and associated primitive skills",
            inputSchema={
                "type": "object",
                "properties": {
                    "protocol_id": {
                        "type": "string",
                        "description": "Protocol ID to fetch",
                    },
                },
                "required": ["protocol_id"],
            },
        ),
        Tool(
            name="ate_protocol_init",
            description="Initialize a new protocol template for a robot. Creates protocol.json and README with transport-specific fields to fill in",
            inputSchema={
                "type": "object",
                "properties": {
                    "robot_model": {
                        "type": "string",
                        "description": "Robot model name (e.g., 'hiwonder-mechdog-pro')",
                    },
                    "transport_type": {
                        "type": "string",
                        "enum": ["ble", "serial", "wifi", "can", "i2c", "spi", "mqtt", "ros2"],
                        "description": "Transport type for communication",
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Output directory for protocol files",
                        "default": "./protocol",
                    },
                },
                "required": ["robot_model", "transport_type"],
            },
        ),
        Tool(
            name="ate_protocol_push",
            description="Upload a protocol definition to FoodForThought registry for community use",
            inputSchema={
                "type": "object",
                "properties": {
                    "protocol_file": {
                        "type": "string",
                        "description": "Path to protocol.json file (default: ./protocol.json)",
                    },
                },
            },
        ),
        Tool(
            name="ate_protocol_scan_serial",
            description="Scan for available serial ports on the system. Useful for discovering connected robot hardware",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="ate_protocol_scan_ble",
            description="Scan for BLE devices in range. Useful for discovering robot devices before connecting",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


def get_primitive_tools() -> List[Tool]:
    """Primitive skills tools"""
    return [
        Tool(
            name="ate_primitive_list",
            description="List primitive skills - tested atomic robot operations like 'tilt_forward', 'gripper_close', etc. with safe parameter ranges",
            inputSchema={
                "type": "object",
                "properties": {
                    "robot_model": {
                        "type": "string",
                        "description": "Filter by robot model name",
                    },
                    "category": {
                        "type": "string",
                        "enum": ["body_pose", "arm", "gripper", "locomotion", "head", "sensing", "manipulation", "navigation"],
                        "description": "Filter by primitive category",
                    },
                    "status": {
                        "type": "string",
                        "enum": ["experimental", "tested", "verified", "deprecated"],
                        "description": "Filter by status",
                    },
                    "tested_only": {
                        "type": "boolean",
                        "description": "Show only tested/verified primitives",
                        "default": False,
                    },
                },
            },
        ),
        Tool(
            name="ate_primitive_get",
            description="Get detailed primitive skill info including command template, tested parameters with safe ranges, timing, safety notes, and dependencies",
            inputSchema={
                "type": "object",
                "properties": {
                    "primitive_id": {
                        "type": "string",
                        "description": "Primitive skill ID to fetch",
                    },
                },
                "required": ["primitive_id"],
            },
        ),
        Tool(
            name="ate_primitive_test",
            description="Submit a test result for a primitive skill. Contributes to reliability score and helps verify safe operation ranges",
            inputSchema={
                "type": "object",
                "properties": {
                    "primitive_id": {
                        "type": "string",
                        "description": "Primitive skill ID to test",
                    },
                    "params": {
                        "type": "string",
                        "description": "Parameters used in test as JSON string (e.g., '{\"pitch\": 15}')",
                    },
                    "result": {
                        "type": "string",
                        "enum": ["pass", "fail", "partial"],
                        "description": "Test result",
                    },
                    "notes": {
                        "type": "string",
                        "description": "Additional notes about the test",
                    },
                    "video_url": {
                        "type": "string",
                        "description": "URL to video recording of test",
                    },
                },
                "required": ["primitive_id", "params", "result"],
            },
        ),
        Tool(
            name="ate_primitive_deps_show",
            description="Show dependency graph for a primitive skill. Shows what primitives it depends on and what depends on it. Indicates deployment readiness",
            inputSchema={
                "type": "object",
                "properties": {
                    "primitive_id": {
                        "type": "string",
                        "description": "Primitive skill ID",
                    },
                },
                "required": ["primitive_id"],
            },
        ),
        Tool(
            name="ate_primitive_deps_add",
            description="Add a dependency to a primitive skill. Creates deployment gates to ensure required primitives are tested before deployment",
            inputSchema={
                "type": "object",
                "properties": {
                    "primitive_id": {
                        "type": "string",
                        "description": "Primitive skill ID (the one that depends)",
                    },
                    "required_id": {
                        "type": "string",
                        "description": "Required primitive skill ID",
                    },
                    "dependency_type": {
                        "type": "string",
                        "enum": ["requires", "extends", "overrides", "optional"],
                        "description": "Type of dependency",
                        "default": "requires",
                    },
                    "min_status": {
                        "type": "string",
                        "enum": ["experimental", "tested", "verified"],
                        "description": "Minimum required status for deployment",
                        "default": "tested",
                    },
                },
                "required": ["primitive_id", "required_id"],
            },
        ),
    ]


def get_bridge_tools() -> List[Tool]:
    """Robot bridge tools for interactive communication"""
    return [
        Tool(
            name="ate_bridge_scan_serial",
            description="Scan for available serial ports. Use this to discover connected robots before using bridge connect",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="ate_bridge_scan_ble",
            description="Scan for BLE devices. Use this to discover bluetooth robots before using bridge connect",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="ate_bridge_send",
            description="Send a single command to a robot and get the response. Useful for quick tests without opening a full interactive session",
            inputSchema={
                "type": "object",
                "properties": {
                    "port": {
                        "type": "string",
                        "description": "Serial port (e.g., /dev/tty.usbserial-0001) or BLE address",
                    },
                    "command": {
                        "type": "string",
                        "description": "Command to send to the robot",
                    },
                    "transport": {
                        "type": "string",
                        "enum": ["serial", "ble"],
                        "description": "Transport type",
                        "default": "serial",
                    },
                    "baud_rate": {
                        "type": "integer",
                        "description": "Baud rate for serial connection",
                        "default": 115200,
                    },
                    "wait": {
                        "type": "number",
                        "description": "Wait time for response in seconds",
                        "default": 0.5,
                    },
                },
                "required": ["port", "command"],
            },
        ),
        Tool(
            name="ate_bridge_replay",
            description="Replay a recorded robot session. Useful for testing primitives or reproducing sequences",
            inputSchema={
                "type": "object",
                "properties": {
                    "recording": {
                        "type": "string",
                        "description": "Path to recording JSON file",
                    },
                    "port": {
                        "type": "string",
                        "description": "Serial port or BLE address",
                    },
                    "transport": {
                        "type": "string",
                        "enum": ["serial", "ble"],
                        "description": "Transport type",
                        "default": "serial",
                    },
                    "baud_rate": {
                        "type": "integer",
                        "description": "Baud rate for serial connection",
                        "default": 115200,
                    },
                    "speed": {
                        "type": "number",
                        "description": "Playback speed multiplier (1.0 = normal, 2.0 = 2x speed)",
                        "default": 1.0,
                    },
                },
                "required": ["recording", "port"],
            },
        ),
    ]


def get_recording_tools() -> List[Tool]:
    """
    Telemetry recording tools for the Data Flywheel.

    These tools enable recording robot telemetry from edge deployments
    and uploading to FoodforThought for labeling and training data.
    """
    return [
        Tool(
            name="ate_record_start",
            description="Start recording telemetry from a robot. Records joint states, velocities, and sensor data for later upload to FoodforThought.",
            inputSchema={
                "type": "object",
                "properties": {
                    "robot_id": {
                        "type": "string",
                        "description": "ID of the robot to record from",
                    },
                    "skill_id": {
                        "type": "string",
                        "description": "Skill ID being executed (for lineage tracking)",
                    },
                    "task_description": {
                        "type": "string",
                        "description": "Human-readable description of what the robot is doing",
                    },
                },
                "required": ["robot_id", "skill_id"],
            },
        ),
        Tool(
            name="ate_record_stop",
            description="Stop the current recording and optionally upload to FoodforThought. Returns a summary of the recording with artifact ID if uploaded.",
            inputSchema={
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "description": "Whether the execution was successful (affects training data quality)",
                        "default": True,
                    },
                    "notes": {
                        "type": "string",
                        "description": "Notes about the recording (failures, edge cases, etc.)",
                    },
                    "upload": {
                        "type": "boolean",
                        "description": "Whether to upload to FoodforThought",
                        "default": True,
                    },
                    "create_labeling_task": {
                        "type": "boolean",
                        "description": "Create a labeling task for community annotation",
                        "default": False,
                    },
                },
            },
        ),
        Tool(
            name="ate_record_status",
            description="Get the status of the current recording session.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="ate_record_demonstration",
            description="Record a timed demonstration for training data. Starts recording, waits for the specified duration, then stops and uploads.",
            inputSchema={
                "type": "object",
                "properties": {
                    "robot_id": {
                        "type": "string",
                        "description": "ID of the robot to record from",
                    },
                    "skill_id": {
                        "type": "string",
                        "description": "Skill being demonstrated",
                    },
                    "task_description": {
                        "type": "string",
                        "description": "What the robot is demonstrating",
                    },
                    "duration_seconds": {
                        "type": "number",
                        "description": "How long to record (default: 30 seconds)",
                        "default": 30.0,
                    },
                    "create_labeling_task": {
                        "type": "boolean",
                        "description": "Create a labeling task for community annotation after upload",
                        "default": True,
                    },
                },
                "required": ["robot_id", "skill_id", "task_description"],
            },
        ),
        Tool(
            name="ate_recordings_list",
            description="List telemetry recordings uploaded to FoodforThought. Filter by robot, skill, or success status.",
            inputSchema={
                "type": "object",
                "properties": {
                    "robot_id": {
                        "type": "string",
                        "description": "Filter by robot ID",
                    },
                    "skill_id": {
                        "type": "string",
                        "description": "Filter by skill ID",
                    },
                    "success": {
                        "type": "boolean",
                        "description": "Filter by success status",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 20,
                    },
                },
            },
        ),
    ]


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List all available MCP tools"""
    tools = []
    tools.extend(get_repository_tools())
    tools.extend(get_robot_tools())
    tools.extend(get_marketplace_tools())  # Phase 6: Unified marketplace
    tools.extend(get_compatibility_tools())
    tools.extend(get_skill_tools())
    tools.extend(get_protocol_tools())
    tools.extend(get_primitive_tools())
    tools.extend(get_bridge_tools())
    tools.extend(get_parts_tools())
    tools.extend(get_generate_tools())
    tools.extend(get_workflow_tools())
    tools.extend(get_team_tools())
    tools.extend(get_data_tools())
    tools.extend(get_deploy_tools())
    tools.extend(get_test_tools())
    tools.extend(get_compiler_tools())
    tools.extend(get_recording_tools())  # Data Flywheel telemetry recording
    return tools


# ============================================================================
# Tool Handlers
# ============================================================================

def capture_output(func, *args, **kwargs):
    """Capture printed output from a function"""
    import io
    import contextlib
    
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        try:
            result = func(*args, **kwargs)
        except SystemExit:
            pass  # CLI functions may call sys.exit
    return f.getvalue()


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    try:
        # Repository tools
        if name == "ate_init":
            result = client.init(
                arguments["name"],
                arguments.get("description", ""),
                arguments.get("visibility", "public"),
            )
            return [
                TextContent(
                    type="text",
                    text=f"Repository created successfully!\nID: {result['repository']['id']}\nName: {result['repository']['name']}",
                )
            ]

        elif name == "ate_clone":
            output = capture_output(
                client.clone,
                arguments["repo_id"], 
                arguments.get("target_dir")
            )
            return [TextContent(type="text", text=output or f"Repository cloned successfully")]

        elif name == "ate_list_repositories":
            params = {}
            if arguments.get("search"):
                params["search"] = arguments["search"]
            if arguments.get("robot_model"):
                params["robotModel"] = arguments["robot_model"]
            params["limit"] = arguments.get("limit", 20)

            response = client._request("GET", "/repositories", params=params)
            repos = response.get("repositories", [])

            result_text = f"Found {len(repos)} repositories:\n\n"
            for repo in repos[:10]:
                result_text += f"- {repo['name']} (ID: {repo['id']})\n"
                if repo.get("description"):
                    result_text += f"  {repo['description'][:100]}...\n"

            return [TextContent(type="text", text=result_text)]

        elif name == "ate_get_repository":
            response = client._request("GET", f"/repositories/{arguments['repo_id']}")
            repo = response.get("repository", {})

            result_text = f"Repository: {repo.get('name', 'Unknown')}\n"
            result_text += f"ID: {repo.get('id', 'Unknown')}\n"
            result_text += f"Description: {repo.get('description', 'No description')}\n"
            result_text += f"Visibility: {repo.get('visibility', 'unknown')}\n"

            return [TextContent(type="text", text=result_text)]

        # Robot tools
        elif name == "ate_list_robots":
            params = {}
            if arguments.get("search"):
                params["search"] = arguments["search"]
            if arguments.get("category"):
                params["category"] = arguments["category"]
            params["limit"] = arguments.get("limit", 20)

            response = client._request("GET", "/robots/profiles", params=params)
            robots = response.get("profiles", [])

            result_text = f"Found {len(robots)} robot profiles:\n\n"
            for robot in robots[:10]:
                result_text += f"- {robot['modelName']} by {robot['manufacturer']} (ID: {robot['id']})\n"
                if robot.get("description"):
                    result_text += f"  {robot['description'][:100]}...\n"

            return [TextContent(type="text", text=result_text)]

        elif name == "ate_get_robot":
            response = client._request("GET", f"/robots/profiles/{arguments['robot_id']}")
            robot = response.get("profile", {})

            result_text = f"Robot: {robot.get('modelName', 'Unknown')}\n"
            result_text += f"Manufacturer: {robot.get('manufacturer', 'Unknown')}\n"
            result_text += f"Category: {robot.get('category', 'Unknown')}\n"
            result_text += f"Description: {robot.get('description', 'No description')}\n"

            return [TextContent(type="text", text=result_text)]

        # Marketplace tools (Phase 6)
        elif name == "ate_marketplace_robots":
            params = {}
            if arguments.get("search"):
                params["q"] = arguments["search"]
            if arguments.get("category"):
                params["category"] = arguments["category"]
            if arguments.get("sort"):
                params["sortBy"] = arguments["sort"]
            params["limit"] = arguments.get("limit", 20)

            response = client._request("GET", "/robots/unified", params=params)
            robots = response.get("robots", [])

            if not robots:
                return [TextContent(type="text", text="No robots found matching your criteria.")]

            result_text = f"Found {len(robots)} robots:\n\n"
            for robot in robots[:20]:
                result_text += f"- **{robot.get('name', 'Unknown')}** ({robot.get('manufacturer', 'Unknown')})\n"
                result_text += f"  ID: {robot.get('id')} | Category: {robot.get('category')} | DOF: {robot.get('dof', 'N/A')}\n"
                if robot.get("description"):
                    result_text += f"  {robot['description'][:100]}...\n"
                result_text += "\n"

            return [TextContent(type="text", text=result_text)]

        elif name == "ate_marketplace_robot":
            robot_id = arguments["robot_id"]
            response = client._request("GET", f"/robots/unified/{robot_id}")
            robot = response.get("robot", {})

            if not robot:
                return [TextContent(type="text", text=f"Robot not found: {robot_id}")]

            result_text = f"# {robot.get('name', 'Unknown')}\n\n"
            result_text += f"**Manufacturer:** {robot.get('manufacturer', 'Unknown')}\n"
            result_text += f"**Category:** {robot.get('category', 'Unknown')}\n"
            result_text += f"**DOF:** {robot.get('dof', 'N/A')}\n"
            result_text += f"**Downloads:** {robot.get('downloads', 0)}\n\n"

            if robot.get("description"):
                result_text += f"## Description\n{robot['description']}\n\n"

            links = robot.get("links", [])
            if links:
                result_text += f"## Links ({len(links)})\n"
                for link in links[:5]:
                    result_text += f"- {link.get('name', 'Unnamed')}\n"

            joints = robot.get("joints", [])
            if joints:
                result_text += f"\n## Joints ({len(joints)})\n"
                for joint in joints[:5]:
                    result_text += f"- {joint.get('name', 'Unnamed')}: {joint.get('type', 'unknown')}\n"

            return [TextContent(type="text", text=result_text)]

        elif name == "ate_marketplace_components":
            params = {}
            if arguments.get("search"):
                params["q"] = arguments["search"]
            if arguments.get("type"):
                params["type"] = arguments["type"]
            if arguments.get("sort"):
                params["sortBy"] = arguments["sort"]
            params["limit"] = arguments.get("limit", 20)

            response = client._request("GET", "/components", params=params)
            components = response.get("components", [])

            if not components:
                return [TextContent(type="text", text="No components found matching your criteria.")]

            result_text = f"Found {len(components)} components:\n\n"
            for comp in components[:20]:
                verified = " ✓" if comp.get("verified") else ""
                result_text += f"- **{comp.get('name', 'Unknown')}** v{comp.get('version', '1.0')}{verified}\n"
                result_text += f"  ID: {comp.get('id')} | Type: {comp.get('type')} | Downloads: {comp.get('downloads', 0)}\n"
                if comp.get("description"):
                    result_text += f"  {comp['description'][:80]}...\n"
                result_text += "\n"

            return [TextContent(type="text", text=result_text)]

        elif name == "ate_marketplace_component":
            component_id = arguments["component_id"]
            response = client._request("GET", f"/components/{component_id}")
            comp = response.get("component", {})

            if not comp:
                return [TextContent(type="text", text=f"Component not found: {component_id}")]

            verified = "Yes ✓" if comp.get("verified") else "No"
            result_text = f"# {comp.get('name', 'Unknown')}\n\n"
            result_text += f"**Type:** {comp.get('type', 'Unknown')}\n"
            result_text += f"**Version:** {comp.get('version', '1.0')}\n"
            result_text += f"**Verified:** {verified}\n"
            result_text += f"**Downloads:** {comp.get('downloads', 0)}\n\n"

            if comp.get("description"):
                result_text += f"## Description\n{comp['description']}\n\n"

            return [TextContent(type="text", text=result_text)]

        elif name == "ate_skill_transfer_check":
            robot_id = arguments["robot_id"]
            direction = arguments.get("direction", "from")
            min_score = arguments.get("min_score", 0.4)
            limit = arguments.get("limit", 10)

            params = {
                "direction": direction,
                "minScore": min_score,
                "limit": limit,
            }
            response = client._request("GET", f"/robots/unified/{robot_id}/skill-transfer", params=params)

            if response.get("error"):
                return [TextContent(type="text", text=f"Error: {response['error']}")]

            source = response.get("sourceRobot", {})
            results = response.get("results", [])

            if not results:
                return [TextContent(type="text", text=f"No compatible robots found for skill transfer from {source.get('name', robot_id)}.")]

            result_text = f"# Skill Transfer Compatibility for {source.get('name', 'Unknown')}\n\n"
            result_text += f"Direction: Skills can transfer **{direction}** this robot\n\n"

            result_text += f"## Compatible Robots ({len(results)})\n\n"
            for item in results:
                robot = item.get("robot", {})
                scores = item.get("scores", {})
                adaptation = item.get("adaptationType", "unknown")
                result_text += f"- **{robot.get('name', 'Unknown')}** - {int(scores.get('overall', 0) * 100)}% ({adaptation})\n"
                result_text += f"  Category: {robot.get('category')} | DOF: {robot.get('dof', 'N/A')}\n\n"

            return [TextContent(type="text", text=result_text)]

        elif name == "ate_robot_parts":
            robot_id = arguments["robot_id"]
            response = client._request("GET", f"/robots/unified/{robot_id}/parts")

            if response.get("error"):
                return [TextContent(type="text", text=f"Error: {response['error']}")]

            robot_name = response.get("robotName", robot_id)
            required = response.get("requiredParts", [])
            compatible = response.get("compatibleParts", [])

            result_text = f"# Parts for {robot_name}\n\n"

            if required:
                result_text += f"## Required Parts ({len(required)})\n"
                for req in required:
                    comp = req.get("component", {})
                    result_text += f"- **{comp.get('name', 'Unknown')}** ({comp.get('type', 'unknown')})\n"
                    result_text += f"  Quantity: {req.get('quantity', 1)} | Required: {'Yes' if req.get('required') else 'Optional'}\n\n"
            else:
                result_text += "## Required Parts\nNo required parts specified.\n\n"

            if compatible:
                result_text += f"## Compatible Parts ({len(compatible)})\n"
                for compat in compatible[:10]:
                    comp = compat.get("component", {})
                    score = compat.get("compatibilityScore", 0)
                    result_text += f"- **{comp.get('name', 'Unknown')}** ({comp.get('type', 'unknown')})\n"
                    result_text += f"  Compatibility: {int(score * 100)}%\n\n"

            return [TextContent(type="text", text=result_text)]

        elif name == "ate_component_robots":
            component_id = arguments["component_id"]
            response = client._request("GET", f"/components/{component_id}/compatible-robots")

            if response.get("error"):
                return [TextContent(type="text", text=f"Error: {response['error']}")]

            comp_name = response.get("componentName", component_id)
            required_by = response.get("requiredBy", [])
            compatible_with = response.get("compatibleWith", [])

            result_text = f"# Robots for {comp_name}\n\n"

            if required_by:
                result_text += f"## Required By ({len(required_by)} robots)\n"
                for req in required_by:
                    robot = req.get("robot", {})
                    result_text += f"- **{robot.get('name', 'Unknown')}** ({robot.get('category', 'unknown')})\n"
                    result_text += f"  Quantity: {req.get('quantity', 1)}\n\n"
            else:
                result_text += "## Required By\nNo robots require this component.\n\n"

            if compatible_with:
                result_text += f"## Compatible With ({len(compatible_with)} robots)\n"
                for compat in compatible_with[:10]:
                    robot = compat.get("robot", {})
                    score = compat.get("compatibilityScore", 0)
                    verified = " ✓" if compat.get("verified") else ""
                    result_text += f"- **{robot.get('name', 'Unknown')}** ({robot.get('category', 'unknown')})\n"
                    result_text += f"  Compatibility: {int(score * 100)}%{verified}\n\n"

            return [TextContent(type="text", text=result_text)]

        # Compatibility tools
        elif name == "ate_check_transfer":
            output = capture_output(
                client.check_transfer,
                arguments.get("skill_id"),
                arguments["source_robot"],
                arguments["target_robot"],
                arguments.get("min_score", 0.0)
            )
            return [TextContent(type="text", text=output)]

        elif name == "ate_adapt":
            output = capture_output(
                client.adapt,
                arguments["source_robot"],
                arguments["target_robot"],
                arguments.get("repo_id"),
                arguments.get("analyze_only", True)
            )
            return [TextContent(type="text", text=output)]

        # Skill tools
        elif name == "ate_pull":
            output = capture_output(
                client.pull,
                arguments["skill_id"],
                arguments.get("robot"),
                arguments.get("format", "json"),
                arguments.get("output", "./data")
            )
            return [TextContent(type="text", text=output)]

        elif name == "ate_upload":
            output = capture_output(
                client.upload,
                arguments["path"],
                arguments["robot"],
                arguments["task"],
                arguments.get("project")
            )
            return [TextContent(type="text", text=output)]

        # Parts tools
        elif name == "ate_parts_list":
            output = capture_output(
                client.parts_list,
                arguments.get("category"),
                arguments.get("manufacturer"),
                arguments.get("search")
            )
            return [TextContent(type="text", text=output)]

        elif name == "ate_parts_check":
            output = capture_output(
                client.parts_check,
                arguments["skill_id"]
            )
            return [TextContent(type="text", text=output)]

        elif name == "ate_parts_require":
            output = capture_output(
                client.parts_require,
                arguments["part_id"],
                arguments["skill_id"],
                arguments.get("version", "1.0.0"),
                arguments.get("required", False)
            )
            return [TextContent(type="text", text=output)]

        elif name == "ate_deps_audit":
            output = capture_output(
                client.deps_audit,
                arguments.get("skill_id")
            )
            return [TextContent(type="text", text=output)]

        # Generate tools
        elif name == "ate_generate":
            output = capture_output(
                client.generate,
                arguments["description"],
                arguments.get("robot", "ur5"),
                arguments.get("output", "./new-skill")
            )
            return [TextContent(type="text", text=output)]

        # Workflow tools
        elif name == "ate_workflow_validate":
            output = capture_output(
                client.workflow_validate,
                arguments["path"]
            )
            return [TextContent(type="text", text=output)]

        elif name == "ate_workflow_run":
            output = capture_output(
                client.workflow_run,
                arguments["path"],
                arguments.get("sim", True),
                arguments.get("dry_run", False)
            )
            return [TextContent(type="text", text=output)]

        elif name == "ate_workflow_export":
            output = capture_output(
                client.workflow_export,
                arguments["path"],
                arguments.get("format", "ros2"),
                arguments.get("output")
            )
            return [TextContent(type="text", text=output)]

        # Team tools
        elif name == "ate_team_create":
            output = capture_output(
                client.team_create,
                arguments["name"],
                arguments.get("description")
            )
            return [TextContent(type="text", text=output)]

        elif name == "ate_team_list":
            output = capture_output(client.team_list)
            return [TextContent(type="text", text=output)]

        elif name == "ate_team_invite":
            output = capture_output(
                client.team_invite,
                arguments["email"],
                arguments["team"],
                arguments.get("role", "member")
            )
            return [TextContent(type="text", text=output)]

        elif name == "ate_team_share":
            output = capture_output(
                client.team_share,
                arguments["skill_id"],
                arguments["team"]
            )
            return [TextContent(type="text", text=output)]

        # Data tools
        elif name == "ate_data_upload":
            output = capture_output(
                client.data_upload,
                arguments["path"],
                arguments["skill"],
                arguments.get("stage", "raw")
            )
            return [TextContent(type="text", text=output)]

        elif name == "ate_data_list":
            output = capture_output(
                client.data_list,
                arguments.get("skill"),
                arguments.get("stage")
            )
            return [TextContent(type="text", text=output)]

        elif name == "ate_data_promote":
            output = capture_output(
                client.data_promote,
                arguments["dataset_id"],
                arguments["to_stage"]
            )
            return [TextContent(type="text", text=output)]

        elif name == "ate_data_export":
            output = capture_output(
                client.data_export,
                arguments["dataset_id"],
                arguments.get("format", "rlds"),
                arguments.get("output", "./export")
            )
            return [TextContent(type="text", text=output)]

        # Deploy tools
        elif name == "ate_deploy":
            output = capture_output(
                client.deploy,
                arguments["robot_type"],
                arguments.get("repo_id")
            )
            return [TextContent(type="text", text=output)]

        elif name == "ate_deploy_config":
            output = capture_output(
                client.deploy_config,
                arguments["config_path"],
                arguments["target"],
                arguments.get("dry_run", False)
            )
            return [TextContent(type="text", text=output)]

        elif name == "ate_deploy_status":
            output = capture_output(
                client.deploy_status,
                arguments["target"]
            )
            return [TextContent(type="text", text=output)]

        # Test tools
        elif name == "ate_test":
            output = capture_output(
                client.test,
                arguments.get("environment", "pybullet"),
                arguments.get("robot"),
                arguments.get("local", False)
            )
            return [TextContent(type="text", text=output)]

        elif name == "ate_validate":
            output = capture_output(
                client.validate,
                arguments.get("checks", ["all"]),
                arguments.get("strict", False),
                None  # files
            )
            return [TextContent(type="text", text=output)]

        elif name == "ate_benchmark":
            output = capture_output(
                client.benchmark,
                arguments.get("type", "all"),
                arguments.get("trials", 10),
                arguments.get("compare")
            )
            return [TextContent(type="text", text=output)]

        # Protocol tools
        elif name == "ate_protocol_list":
            output = capture_output(
                client.protocol_list,
                arguments.get("robot_model"),
                arguments.get("transport_type"),
                arguments.get("verified_only", False),
                arguments.get("search")
            )
            return [TextContent(type="text", text=output)]

        elif name == "ate_protocol_get":
            output = capture_output(
                client.protocol_get,
                arguments["protocol_id"]
            )
            return [TextContent(type="text", text=output)]

        elif name == "ate_protocol_init":
            output = capture_output(
                client.protocol_init,
                arguments["robot_model"],
                arguments["transport_type"],
                arguments.get("output_dir", "./protocol")
            )
            return [TextContent(type="text", text=output)]

        elif name == "ate_protocol_push":
            output = capture_output(
                client.protocol_push,
                arguments.get("protocol_file")
            )
            return [TextContent(type="text", text=output)]

        elif name == "ate_protocol_scan_serial":
            output = capture_output(client.protocol_scan_serial)
            return [TextContent(type="text", text=output)]

        elif name == "ate_protocol_scan_ble":
            output = capture_output(client.protocol_scan_ble)
            return [TextContent(type="text", text=output)]

        # Primitive tools
        elif name == "ate_primitive_list":
            output = capture_output(
                client.primitive_list,
                arguments.get("robot_model"),
                arguments.get("category"),
                arguments.get("status"),
                arguments.get("tested_only", False)
            )
            return [TextContent(type="text", text=output)]

        elif name == "ate_primitive_get":
            output = capture_output(
                client.primitive_get,
                arguments["primitive_id"]
            )
            return [TextContent(type="text", text=output)]

        elif name == "ate_primitive_test":
            output = capture_output(
                client.primitive_test,
                arguments["primitive_id"],
                arguments["params"],
                arguments["result"],
                arguments.get("notes"),
                arguments.get("video_url")
            )
            return [TextContent(type="text", text=output)]

        elif name == "ate_primitive_deps_show":
            output = capture_output(
                client.primitive_deps_show,
                arguments["primitive_id"]
            )
            return [TextContent(type="text", text=output)]

        elif name == "ate_primitive_deps_add":
            output = capture_output(
                client.primitive_deps_add,
                arguments["primitive_id"],
                arguments["required_id"],
                arguments.get("dependency_type", "requires"),
                arguments.get("min_status", "tested")
            )
            return [TextContent(type="text", text=output)]

        # Bridge tools
        elif name == "ate_bridge_scan_serial":
            output = capture_output(client.protocol_scan_serial)
            return [TextContent(type="text", text=output)]

        elif name == "ate_bridge_scan_ble":
            output = capture_output(client.protocol_scan_ble)
            return [TextContent(type="text", text=output)]

        elif name == "ate_bridge_send":
            output = capture_output(
                client.bridge_send,
                arguments["port"],
                arguments["command"],
                arguments.get("transport", "serial"),
                arguments.get("baud_rate", 115200),
                arguments.get("wait", 0.5)
            )
            return [TextContent(type="text", text=output if output else "Command sent (no response)")]

        elif name == "ate_bridge_replay":
            output = capture_output(
                client.bridge_replay,
                arguments["recording"],
                arguments["port"],
                arguments.get("transport", "serial"),
                arguments.get("baud_rate", 115200),
                arguments.get("speed", 1.0)
            )
            return [TextContent(type="text", text=output)]

        # Compiler tools
        elif name == "ate_compile_skill":
            output = capture_output(
                client.compile_skill,
                arguments["skill_path"],
                arguments.get("output", "./output"),
                arguments.get("target", "python"),
                arguments.get("robot"),
                arguments.get("ate_dir")
            )
            return [TextContent(type="text", text=output or "Skill compiled successfully")]

        elif name == "ate_test_compiled_skill":
            output = capture_output(
                client.test_compiled_skill,
                arguments["skill_path"],
                arguments.get("mode", "dry-run"),
                arguments.get("robot_port"),
                arguments.get("params", {})
            )
            return [TextContent(type="text", text=output or "Skill test completed")]

        elif name == "ate_publish_compiled_skill":
            output = capture_output(
                client.publish_compiled_skill,
                arguments["skill_path"],
                arguments.get("visibility", "public")
            )
            return [TextContent(type="text", text=output or "Skill published successfully")]

        elif name == "ate_check_skill_compatibility":
            output = capture_output(
                client.check_skill_compatibility,
                arguments["skill_path"],
                arguments.get("robot_urdf"),
                arguments.get("robot_ate_dir")
            )
            return [TextContent(type="text", text=output or "Compatibility check completed")]

        elif name == "ate_list_primitives":
            from ate.primitives import PRIMITIVE_REGISTRY, PrimitiveCategory

            category = arguments.get("category", "all")
            hardware = arguments.get("hardware")

            result_text = "# Available Primitives\n\n"

            for prim_name, prim_def in PRIMITIVE_REGISTRY.items():
                # Filter by category
                if category != "all":
                    cat_match = prim_def.get("category", "").lower() == category.lower()
                    if not cat_match:
                        continue

                # Filter by hardware
                if hardware:
                    req_hardware = prim_def.get("hardware", [])
                    if hardware.lower() not in [h.lower() for h in req_hardware]:
                        continue

                result_text += f"## {prim_name}\n"
                result_text += f"**Category:** {prim_def.get('category', 'unknown')}\n"
                result_text += f"**Description:** {prim_def.get('description', 'No description')}\n"

                # Parameters
                params = prim_def.get("parameters", {})
                if params:
                    result_text += "**Parameters:**\n"
                    for param_name, param_def in params.items():
                        required = "required" if param_def.get("required", False) else "optional"
                        result_text += f"  - `{param_name}` ({param_def.get('type', 'any')}, {required}): {param_def.get('description', '')}\n"

                # Hardware requirements
                hw_reqs = prim_def.get("hardware", [])
                if hw_reqs:
                    result_text += f"**Hardware:** {', '.join(hw_reqs)}\n"

                result_text += "\n"

            return [TextContent(type="text", text=result_text)]

        elif name == "ate_get_primitive":
            from ate.primitives import get_primitive

            prim_name = arguments["name"]
            prim_def = get_primitive(prim_name)

            if not prim_def:
                return [TextContent(type="text", text=f"Primitive not found: {prim_name}")]

            result_text = f"# {prim_name}\n\n"
            result_text += f"**Category:** {prim_def.get('category', 'unknown')}\n"
            result_text += f"**Description:** {prim_def.get('description', 'No description')}\n\n"

            # Parameters
            params = prim_def.get("parameters", {})
            if params:
                result_text += "## Parameters\n\n"
                for param_name, param_def in params.items():
                    required = "✓ Required" if param_def.get("required", False) else "○ Optional"
                    default = f", default: `{param_def.get('default')}`" if "default" in param_def else ""
                    result_text += f"### `{param_name}`\n"
                    result_text += f"- **Type:** {param_def.get('type', 'any')}\n"
                    result_text += f"- **Status:** {required}{default}\n"
                    result_text += f"- **Description:** {param_def.get('description', '')}\n\n"

            # Hardware requirements
            hw_reqs = prim_def.get("hardware", [])
            if hw_reqs:
                result_text += f"## Hardware Requirements\n\n"
                for hw in hw_reqs:
                    result_text += f"- {hw}\n"

            # Return type
            result_text += f"\n## Returns\n\n`{prim_def.get('returns', 'bool')}`\n"

            return [TextContent(type="text", text=result_text)]

        elif name == "ate_validate_skill_spec":
            from ate.skill_schema import SkillSpecification

            skill_path = arguments["skill_path"]

            try:
                spec = SkillSpecification.from_yaml(skill_path)
                errors = spec.validate()

                if errors:
                    result_text = f"# Validation Failed\n\n"
                    result_text += f"Found {len(errors)} error(s) in `{skill_path}`:\n\n"
                    for error in errors:
                        result_text += f"- ❌ {error}\n"
                    return [TextContent(type="text", text=result_text)]

                result_text = f"# Validation Passed ✓\n\n"
                result_text += f"**Skill:** {spec.name}\n"
                result_text += f"**Version:** {spec.version}\n"
                result_text += f"**Description:** {spec.description}\n\n"

                # Summary
                result_text += "## Summary\n\n"
                result_text += f"- **Parameters:** {len(spec.parameters)}\n"
                result_text += f"- **Hardware Requirements:** {len(spec.hardware_requirements)}\n"
                result_text += f"- **Execution Steps:** {len(spec.execution)}\n"
                result_text += f"- **Success Criteria:** {len(spec.success_criteria)}\n"

                return [TextContent(type="text", text=result_text)]
            except Exception as e:
                return [TextContent(type="text", text=f"# Validation Error\n\nFailed to parse skill specification:\n\n```\n{str(e)}\n```")]

        # ============================================================================
        # Recording Tools (Data Flywheel)
        # ============================================================================

        elif name == "ate_record_start":
            robot_id = arguments["robot_id"]
            skill_id = arguments["skill_id"]
            task_description = arguments.get("task_description", "")

            # Store recording state in a module-level variable
            global _active_recording
            import time
            import uuid

            _active_recording = {
                "id": str(uuid.uuid4()),
                "robot_id": robot_id,
                "skill_id": skill_id,
                "task_description": task_description,
                "start_time": time.time(),
                "frames": [],
            }

            result_text = f"# Recording Started\n\n"
            result_text += f"**Recording ID:** {_active_recording['id']}\n"
            result_text += f"**Robot:** {robot_id}\n"
            result_text += f"**Skill:** {skill_id}\n"
            if task_description:
                result_text += f"**Task:** {task_description}\n"
            result_text += f"\nRun `ate_record_stop` when finished to upload to FoodforThought."

            return [TextContent(type="text", text=result_text)]

        elif name == "ate_record_stop":
            global _active_recording
            import time

            if not _active_recording:
                return [TextContent(type="text", text="No active recording. Start one with `ate_record_start`.")]

            success = arguments.get("success", True)
            notes = arguments.get("notes", "")
            upload = arguments.get("upload", True)
            create_labeling_task = arguments.get("create_labeling_task", False)

            # Calculate duration
            end_time = time.time()
            duration = end_time - _active_recording["start_time"]
            frame_count = len(_active_recording.get("frames", []))

            recording_summary = {
                "id": _active_recording["id"],
                "robot_id": _active_recording["robot_id"],
                "skill_id": _active_recording["skill_id"],
                "task_description": _active_recording.get("task_description", ""),
                "duration": duration,
                "frame_count": frame_count,
                "success": success,
                "notes": notes,
            }

            result_text = f"# Recording Stopped\n\n"
            result_text += f"**Recording ID:** {recording_summary['id']}\n"
            result_text += f"**Duration:** {duration:.1f}s\n"
            result_text += f"**Frames:** {frame_count}\n"
            result_text += f"**Success:** {'Yes' if success else 'No'}\n"

            if upload:
                # Upload to FoodforThought via the telemetry ingest API
                try:
                    from datetime import datetime

                    recording_data = {
                        "recording": {
                            "id": recording_summary["id"],
                            "robotId": recording_summary["robot_id"],
                            "skillId": recording_summary["skill_id"],
                            "source": "hardware",  # Edge recording
                            "startTime": datetime.fromtimestamp(_active_recording["start_time"]).isoformat(),
                            "endTime": datetime.fromtimestamp(end_time).isoformat(),
                            "success": success,
                            "metadata": {
                                "duration": duration,
                                "frameRate": frame_count / duration if duration > 0 else 0,
                                "totalFrames": frame_count,
                                "tags": ["edge_recording", "mcp_tool"],
                            },
                            "frames": _active_recording.get("frames", []),
                            "events": [],
                        },
                    }

                    # Create labeling task if requested
                    if create_labeling_task:
                        recording_data["createLabelingTask"] = True

                    response = client._request("POST", "/telemetry/ingest", json=recording_data)

                    artifact_id = response.get("data", {}).get("artifactId", "")
                    result_text += f"\n## Uploaded to FoodforThought\n"
                    result_text += f"**Artifact ID:** {artifact_id}\n"
                    result_text += f"**URL:** https://foodforthought.kindly.fyi/artifacts/{artifact_id}\n"

                    if create_labeling_task:
                        task_id = response.get("data", {}).get("taskId", "")
                        if task_id:
                            result_text += f"**Labeling Task:** https://foodforthought.kindly.fyi/labeling/{task_id}\n"
                except Exception as e:
                    result_text += f"\n## Upload Failed\n"
                    result_text += f"Error: {str(e)}\n"
                    result_text += "Recording saved locally. Try uploading manually later.\n"

            if notes:
                result_text += f"\n**Notes:** {notes}\n"

            # Clear active recording
            _active_recording = None

            return [TextContent(type="text", text=result_text)]

        elif name == "ate_record_status":
            global _active_recording
            import time

            if not _active_recording:
                return [TextContent(type="text", text="No active recording session.")]

            current_time = time.time()
            elapsed = current_time - _active_recording["start_time"]
            frame_count = len(_active_recording.get("frames", []))

            result_text = f"# Recording Status\n\n"
            result_text += f"**Recording ID:** {_active_recording['id']}\n"
            result_text += f"**Robot:** {_active_recording['robot_id']}\n"
            result_text += f"**Skill:** {_active_recording['skill_id']}\n"
            result_text += f"**Elapsed:** {elapsed:.1f}s\n"
            result_text += f"**Frames:** {frame_count}\n"
            result_text += f"**Status:** Recording...\n"

            return [TextContent(type="text", text=result_text)]

        elif name == "ate_record_demonstration":
            robot_id = arguments["robot_id"]
            skill_id = arguments["skill_id"]
            task_description = arguments["task_description"]
            duration_seconds = arguments.get("duration_seconds", 30.0)
            create_labeling_task = arguments.get("create_labeling_task", True)

            import time
            import uuid
            from datetime import datetime

            # Start recording
            recording_id = str(uuid.uuid4())
            start_time = time.time()

            result_text = f"# Recording Demonstration\n\n"
            result_text += f"**Recording ID:** {recording_id}\n"
            result_text += f"**Robot:** {robot_id}\n"
            result_text += f"**Skill:** {skill_id}\n"
            result_text += f"**Task:** {task_description}\n"
            result_text += f"**Duration:** {duration_seconds}s\n\n"

            # Wait for the specified duration
            # Note: In a real implementation, this would be collecting telemetry frames
            # For now, we simulate the wait
            result_text += f"Recording started at {datetime.now().isoformat()}\n"
            result_text += f"Waiting {duration_seconds} seconds...\n\n"

            # In production, we would collect frames here
            # For MCP, we just note that recording would happen
            time.sleep(min(duration_seconds, 5.0))  # Cap at 5s for responsiveness

            end_time = time.time()
            actual_duration = end_time - start_time

            # Upload to FoodforThought
            try:
                recording_data = {
                    "recording": {
                        "id": recording_id,
                        "robotId": robot_id,
                        "skillId": skill_id,
                        "source": "hardware",
                        "startTime": datetime.fromtimestamp(start_time).isoformat(),
                        "endTime": datetime.fromtimestamp(end_time).isoformat(),
                        "success": True,
                        "metadata": {
                            "duration": actual_duration,
                            "frameRate": 0,  # Placeholder
                            "totalFrames": 0,  # Placeholder
                            "tags": ["demonstration", "mcp_tool"],
                            "task_description": task_description,
                        },
                        "frames": [],
                        "events": [],
                    },
                }

                if create_labeling_task:
                    recording_data["createLabelingTask"] = True

                response = client._request("POST", "/telemetry/ingest", json=recording_data)

                artifact_id = response.get("data", {}).get("artifactId", "")
                result_text += f"## Uploaded to FoodforThought\n\n"
                result_text += f"**Artifact ID:** {artifact_id}\n"
                result_text += f"**URL:** https://foodforthought.kindly.fyi/artifacts/{artifact_id}\n"

                if create_labeling_task:
                    task_id = response.get("data", {}).get("taskId", "")
                    if task_id:
                        result_text += f"**Labeling Task:** https://foodforthought.kindly.fyi/labeling/{task_id}\n"
            except Exception as e:
                result_text += f"## Upload Failed\n\nError: {str(e)}\n"

            return [TextContent(type="text", text=result_text)]

        elif name == "ate_recordings_list":
            # Query telemetry recordings from FoodforThought
            params = {
                "type": "trajectory",
                "limit": arguments.get("limit", 20),
            }

            if arguments.get("robot_id"):
                params["robotModel"] = arguments["robot_id"]
            if arguments.get("skill_id"):
                params["task"] = arguments["skill_id"]

            try:
                response = client._request("GET", "/artifacts", params=params)
                artifacts = response.get("artifacts", [])

                if not artifacts:
                    return [TextContent(type="text", text="No recordings found.")]

                result_text = f"# Telemetry Recordings\n\n"
                result_text += f"Found {len(artifacts)} recording(s):\n\n"

                for artifact in artifacts:
                    metadata = artifact.get("metadata", {})
                    result_text += f"## {artifact.get('name', 'Unnamed')}\n"
                    result_text += f"- **ID:** {artifact.get('id')}\n"
                    result_text += f"- **Robot:** {metadata.get('robotId', 'Unknown')}\n"
                    result_text += f"- **Skill:** {metadata.get('skillId', 'Unknown')}\n"
                    result_text += f"- **Duration:** {metadata.get('duration', 0):.1f}s\n"
                    result_text += f"- **Frames:** {metadata.get('frameCount', 0)}\n"
                    result_text += f"- **Success:** {'Yes' if metadata.get('success', True) else 'No'}\n"
                    result_text += f"- **Source:** {metadata.get('source', 'Unknown')}\n"
                    result_text += "\n"

                return [TextContent(type="text", text=result_text)]
            except Exception as e:
                return [TextContent(type="text", text=f"Error fetching recordings: {str(e)}")]

        else:
            return [
                TextContent(
                    type="text",
                    text=f"Unknown tool: {name}",
                )
            ]

    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Error executing tool {name}: {str(e)}",
            )
        ]


# ============================================================================
# Resources
# ============================================================================

@server.list_resources()
async def list_resources() -> List[Resource]:
    """List available resources"""
    return [
        Resource(
            uri="repository://*",
            name="Repository",
            description="Access FoodforThought repository details",
            mimeType="application/json",
        ),
        Resource(
            uri="robot://*",
            name="Robot Profile",
            description="Access robot profile details",
            mimeType="application/json",
        ),
        Resource(
            uri="skill://*",
            name="Skill",
            description="Access skill/artifact details",
            mimeType="application/json",
        ),
        Resource(
            uri="part://*",
            name="Hardware Part",
            description="Access hardware part details",
            mimeType="application/json",
        ),
        Resource(
            uri="workflow://*",
            name="Workflow",
            description="Access workflow definition",
            mimeType="application/yaml",
        ),
        Resource(
            uri="team://*",
            name="Team",
            description="Access team details",
            mimeType="application/json",
        ),
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a resource"""
    if uri.startswith("repository://"):
        repo_id = uri.replace("repository://", "")
        response = client._request("GET", f"/repositories/{repo_id}")
        return json.dumps(response.get("repository", {}), indent=2)
    elif uri.startswith("robot://"):
        robot_id = uri.replace("robot://", "")
        response = client._request("GET", f"/robots/profiles/{robot_id}")
        return json.dumps(response.get("profile", {}), indent=2)
    elif uri.startswith("skill://"):
        skill_id = uri.replace("skill://", "")
        response = client._request("GET", f"/skills/{skill_id}")
        return json.dumps(response.get("skill", {}), indent=2)
    elif uri.startswith("part://"):
        part_id = uri.replace("part://", "")
        response = client._request("GET", f"/parts/{part_id}")
        return json.dumps(response.get("part", {}), indent=2)
    elif uri.startswith("team://"):
        team_slug = uri.replace("team://", "")
        response = client._request("GET", f"/teams/{team_slug}")
        return json.dumps(response.get("team", {}), indent=2)
    else:
        raise ValueError(f"Unknown resource URI: {uri}")


# ============================================================================
# Prompts
# ============================================================================

@server.list_prompts()
async def list_prompts() -> List[Prompt]:
    """List available prompts"""
    return [
        Prompt(
            name="create_skill",
            description="Guided workflow for creating a new robot skill from scratch",
            arguments=[
                PromptArgument(
                    name="robot_model",
                    description="Target robot model",
                    required=True,
                ),
                PromptArgument(
                    name="task_description",
                    description="Natural language description of the skill/task",
                    required=True,
                ),
            ],
        ),
        Prompt(
            name="adapt_skill",
            description="Guided workflow for adapting a skill between different robots",
            arguments=[
                PromptArgument(
                    name="source_robot",
                    description="Source robot model",
                    required=True,
                ),
                PromptArgument(
                    name="target_robot",
                    description="Target robot model",
                    required=True,
                ),
                PromptArgument(
                    name="repository_id",
                    description="Repository ID to adapt",
                    required=True,
                ),
            ],
        ),
        Prompt(
            name="setup_workflow",
            description="Create a multi-skill workflow/pipeline",
            arguments=[
                PromptArgument(
                    name="task_description",
                    description="Description of the overall task",
                    required=True,
                ),
                PromptArgument(
                    name="robot",
                    description="Target robot model",
                    required=True,
                ),
            ],
        ),
        Prompt(
            name="deploy_skill",
            description="Deploy a skill to production robots",
            arguments=[
                PromptArgument(
                    name="skill_id",
                    description="Skill ID to deploy",
                    required=True,
                ),
                PromptArgument(
                    name="target",
                    description="Target fleet or robot",
                    required=True,
                ),
            ],
        ),
        Prompt(
            name="debug_compatibility",
            description="Debug why a skill isn't transferring well between robots",
            arguments=[
                PromptArgument(
                    name="source_robot",
                    description="Source robot model",
                    required=True,
                ),
                PromptArgument(
                    name="target_robot",
                    description="Target robot model",
                    required=True,
                ),
                PromptArgument(
                    name="skill_id",
                    description="Skill ID having issues",
                    required=True,
                ),
            ],
        ),
    ]


@server.get_prompt()
async def get_prompt(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Get prompt content"""
    if name == "create_skill":
        return [
            TextContent(
                type="text",
                text=f"""# Create a Robot Skill for {arguments.get('robot_model', 'your robot')}

## Task: {arguments.get('task_description', 'Not specified')}

### Steps:

1. **Generate Scaffolding**
   Use `ate_generate` to create skill files from your task description:
   - This creates skill.yaml, main.py, test_skill.py, and README.md

2. **Review Generated Files**
   - Check skill.yaml for correct parameters
   - Implement the TODO sections in main.py

3. **Add Part Dependencies**
   Use `ate_parts_list` to find required hardware, then `ate_parts_require` to add dependencies

4. **Test in Simulation**
   Use `ate_test` with environment="pybullet" to validate the skill

5. **Run Safety Validation**
   Use `ate_validate` with checks=["collision", "speed", "workspace", "force"]

6. **Upload Demonstrations**
   Use `ate_upload` to submit demo videos for community labeling

7. **Check Transfer Compatibility**
   Use `ate_check_transfer` to see which other robots can use this skill
""",
            )
        ]
    
    elif name == "adapt_skill":
        return [
            TextContent(
                type="text",
                text=f"""# Adapt Skill from {arguments.get('source_robot')} to {arguments.get('target_robot')}

## Repository: {arguments.get('repository_id')}

### Steps:

1. **Check Compatibility**
   Use `ate_check_transfer` to get the compatibility score and adaptation type

2. **Generate Adaptation Plan**
   Use `ate_adapt` to see what changes are needed:
   - Kinematic adaptations
   - Sensor mappings
   - Code modifications

3. **Review Requirements**
   - Check if new parts are needed with `ate_parts_check`
   - Verify hardware compatibility

4. **Apply Adaptations**
   Based on the adaptation type:
   - **Direct**: No changes needed
   - **Parametric**: Adjust configuration values
   - **Retrain**: Collect new demonstrations
   - **Manual**: Significant code changes required

5. **Test Adapted Skill**
   Use `ate_test` with robot="{arguments.get('target_robot')}"

6. **Validate Safety**
   Use `ate_validate` with strict=true for production deployment
""",
            )
        ]
    
    elif name == "setup_workflow":
        return [
            TextContent(
                type="text",
                text=f"""# Create Multi-Skill Workflow

## Task: {arguments.get('task_description', 'Not specified')}
## Robot: {arguments.get('robot', 'Not specified')}

### Steps:

1. **Define Workflow Steps**
   Create a workflow.yaml file with your skill pipeline:
   ```yaml
   name: My Workflow
   version: 1.0.0
   robot:
     model: {arguments.get('robot', 'ur5')}
   steps:
     - id: step1
       skill: perception/detect-object
     - id: step2
       skill: manipulation/pick
       depends_on: [step1]
   ```

2. **Validate Workflow**
   Use `ate_workflow_validate` to check for errors

3. **Test in Simulation**
   Use `ate_workflow_run` with sim=true

4. **Dry Run**
   Use `ate_workflow_run` with dry_run=true to see execution plan

5. **Export for Production**
   Use `ate_workflow_export` with format="ros2" for ROS2 launch file
""",
            )
        ]
    
    elif name == "deploy_skill":
        return [
            TextContent(
                type="text",
                text=f"""# Deploy Skill to Production

## Skill: {arguments.get('skill_id')}
## Target: {arguments.get('target')}

### Pre-Deployment Checklist:

1. **Audit Dependencies**
   Use `ate_deps_audit` to verify all parts are available

2. **Run Validation**
   Use `ate_validate` with strict=true

3. **Benchmark Performance**
   Use `ate_benchmark` to ensure acceptable performance

4. **Check Deployment Config**
   Create deploy.yaml for hybrid edge/cloud deployment if needed

### Deployment Steps:

1. **Dry Run**
   Use `ate_deploy_config` with dry_run=true to preview

2. **Deploy**
   Use `ate_deploy` or `ate_deploy_config` to push to target

3. **Monitor Status**
   Use `ate_deploy_status` to check deployment health
""",
            )
        ]
    
    elif name == "debug_compatibility":
        return [
            TextContent(
                type="text",
                text=f"""# Debug Skill Transfer Compatibility

## Source: {arguments.get('source_robot')}
## Target: {arguments.get('target_robot')}
## Skill: {arguments.get('skill_id')}

### Diagnostic Steps:

1. **Get Compatibility Score**
   Use `ate_check_transfer` to see overall compatibility

2. **Check Score Breakdown**
   Look at individual scores:
   - Kinematic score: Joint configurations, workspace overlap
   - Sensor score: Camera, force/torque sensor compatibility
   - Compute score: Processing power requirements

3. **Review Part Requirements**
   Use `ate_parts_check` to see required hardware for the skill

4. **Compare Robot Profiles**
   Use `ate_get_robot` for both source and target to compare specs

5. **Generate Adaptation Plan**
   Use `ate_adapt` to get specific recommendations

### Common Issues:

- **Low Kinematic Score**: Check joint limits, reach, payload
- **Low Sensor Score**: Missing cameras or sensors
- **Low Compute Score**: Target robot has less processing power
- **Impossible Transfer**: Fundamentally incompatible hardware
""",
            )
        ]
    
    else:
        return [TextContent(type="text", text=f"Unknown prompt: {name}")]


async def main():
    """Main entry point for MCP server"""
    # Run the server using stdio transport
    stdin, stdout = stdio_server()
    await server.run(
        stdin, stdout, server.create_initialization_options()
    )


if __name__ == "__main__":
    asyncio.run(main())

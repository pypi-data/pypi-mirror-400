# FoodforThought CLI

GitHub-like CLI tool for the FoodforThought robotics repository platform.

**Version**: 0.2.1  
**PyPI**: https://pypi.org/project/foodforthought-cli/

## Installation

```bash
pip install foodforthought-cli
```

Or install from source:

```bash
cd foodforthought-cli
pip install -e .
```

## Configuration

Set environment variables:

```bash
export ATE_API_URL="https://kindly.fyi/api"
export ATE_API_KEY="your-api-key-here"
```

## Usage

### Initialize a repository

```bash
ate init my-robot-skill -d "A skill for my robot" -v public
```

### Clone a repository

```bash
ate clone <repository-id>
```

### Create a commit

```bash
ate commit -m "Add new control algorithm"
```

### Push to remote

```bash
ate push -b main
```

### Deploy to robot

```bash
ate deploy unitree-r1
```

## Commands

### Repository Management
- `ate init <name>` - Initialize a new repository
- `ate clone <repo-id>` - Clone a repository
- `ate commit -m <message>` - Create a commit
- `ate push [-b <branch>]` - Push commits to remote

### Skill Pipeline
- `ate pull <skill-id> [--robot <robot>] [--format json|rlds|lerobot] [--output ./data]` - Pull skill data for training
- `ate upload <video-path> --robot <robot> --task <task> [--project <id>]` - Upload demonstrations for labeling
- `ate check-transfer --from <source-robot> --to <target-robot> [--skill <id>]` - Check skill transfer compatibility
- `ate labeling-status <job-id>` - Check labeling job status

### Parts & Dependencies (New in v0.2.0)
- `ate parts list [--category gripper]` - List available hardware parts
- `ate parts check <skill-id>` - Check part compatibility for a skill
- `ate parts require <part-id> --skill <skill-id>` - Add part dependency to a skill
- `ate deps audit` - Verify all dependencies are compatible

### Text-to-Skill Generation (New in v0.2.0)
- `ate generate "<description>" --robot <robot> --output ./skill/` - Generate skill skeleton from natural language

Example:
```bash
ate generate "pick up box and place on pallet" --robot franka-panda --output ./new-skill/
```

### Workflow Orchestration (New in v0.2.0)
- `ate workflow validate <pipeline.yaml>` - Validate a workflow definition
- `ate workflow run <pipeline.yaml> --sim` - Run workflow in simulation
- `ate workflow export <pipeline.yaml> --format ros2` - Export to ROS2 launch format

### Team Collaboration (New in v0.2.0)
- `ate team create <name>` - Create a new team
- `ate team invite <email> --role member` - Invite a member
- `ate team list` - List teams and members
- `ate skill share <skill-id> --team <team-slug>` - Share a skill with a team

### Skill Compiler (New in v0.2.1)

Compile skill.yaml specifications into deployable packages. See [docs/SKILL_COMPILER.md](docs/SKILL_COMPILER.md) for full documentation.

```bash
# Validate a skill specification
ate validate-skill my_skill.skill.yaml

# Compile to Python package
ate compile my_skill.skill.yaml --target python --output ./dist

# Compile to ROS2 package
ate compile my_skill.skill.yaml --target ros2 --robot robots/ur5.urdf

# Test the compiled skill
ate test-skill ./dist --mode dry-run

# Check robot compatibility
ate check-compatibility my_skill.skill.yaml --robot-urdf robots/ur5.urdf

# Publish to registry
ate publish-skill ./dist --visibility public
```

**Quick Start for AI Assistants:**
1. `ate_list_primitives` - Discover available building blocks
2. `ate_validate_skill_spec` - Check skill.yaml for errors
3. `ate_check_skill_compatibility` - Verify robot compatibility
4. `ate_compile_skill` - Generate deployable code
5. `ate_test_compiled_skill` - Test without a robot

### Dataset Management (New in v0.2.0)
- `ate data upload ./sensor-logs/ --skill <id> --stage raw` - Upload sensor data
- `ate data list --skill <id> --stage annotated` - List datasets
- `ate data promote <dataset-id> --to skill-abstracted` - Promote to next stage
- `ate data export <dataset-id> --format rlds` - Export dataset

### Deployment & Configuration (New in v0.2.0)
- `ate deploy --config deploy.yaml --target fleet-alpha` - Deploy with config
- `ate deploy status <fleet-name>` - Check deployment status

### Deployment & Testing
- `ate deploy <robot-type>` - Deploy to a robot (e.g., unitree-r1)
- `ate test [-e gazebo|mujoco|pybullet|webots] [-r robot]` - Test skills in simulation
- `ate benchmark [-t speed|accuracy|robustness|efficiency|all]` - Run performance benchmarks
- `ate adapt <source-robot> <target-robot>` - Adapt skills between robots

### Safety & Validation
- `ate validate [-c collision|speed|workspace|force|all]` - Validate safety and compliance
- `ate stream [start|stop|status] [-s sensors...]` - Stream sensor data

## Cursor IDE Integration (MCP)

FoodforThought CLI includes a full MCP (Model Context Protocol) server for integration with Cursor IDE.

### Quick Install via Deep Link

Click this link to install in Cursor:
```
cursor://anysphere.cursor-deeplink/mcp/install?name=foodforthought&config=eyJtY3BTZXJ2ZXJzIjogeyJmb29kZm9ydGhvdWdodCI6IHsiY29tbWFuZCI6ICJweXRob24iLCAiYXJncyI6IFsiLW0iLCAiYXRlLm1jcF9zZXJ2ZXIiXSwgImVudiI6IHsiQVRFX0FQSV9VUkwiOiAiaHR0cHM6Ly9raW5kbHkuZnlpL2FwaSJ9fX19
```

### Manual Installation

1. Install the CLI:
   ```bash
   pip install foodforthought-cli
   ```

2. Install MCP SDK:
   ```bash
   pip install mcp
   ```

3. Add to your Cursor MCP config (`~/.cursor/mcp.json` or `.cursor/mcp.json`):
   ```json
   {
     "mcpServers": {
       "foodforthought": {
         "command": "python",
         "args": ["-m", "ate.mcp_server"],
         "env": {
           "ATE_API_URL": "https://kindly.fyi/api"
         }
       }
     }
   }
   ```

4. Restart Cursor

### Available MCP Tools (37+)

| Category | Tools |
|----------|-------|
| **Skill Compiler** | `ate_compile_skill`, `ate_validate_skill_spec`, `ate_test_compiled_skill`, `ate_publish_compiled_skill`, `ate_check_skill_compatibility` |
| **Primitives** | `ate_list_primitives`, `ate_get_primitive` |
| **Skills** | `ate_skills_list`, `ate_skills_create`, `ate_skills_get`, `ate_pull`, `ate_upload` |
| **Testing** | `ate_test`, `ate_simulate` |
| **Compatibility** | `ate_adapt`, `ate_compatibility_check` |
| **Parts** | `ate_parts_list`, `ate_parts_check`, `ate_parts_require`, `ate_deps_audit` |
| **Generation** | `ate_generate` |
| **Workflows** | `ate_workflow_validate`, `ate_workflow_run`, `ate_workflow_export` |
| **Teams** | `ate_team_create`, `ate_team_invite`, `ate_team_list`, `ate_team_share` |
| **Datasets** | `ate_data_upload`, `ate_data_list`, `ate_data_promote`, `ate_data_export` |
| **Deployment** | `ate_deploy`, `ate_deploy_status` |
| **Audit** | `ate_audit_trail` |

### MCP Resources

- `skill://{id}` - Skill details and configuration
- `part://{id}` - Hardware part specifications
- `workflow://{id}` - Workflow definition
- `team://{id}` - Team information
- `deployment://{id}` - Deployment status
- `audit://{id}` - Audit trail

### MCP Prompts

- `setup_workflow` - Guide for multi-skill workflows
- `deploy_skill` - Step-by-step deployment guide
- `debug_compatibility` - Debug skill transfer issues
- `onboard_robot` - Add a new robot to the platform
- `audit_deployment` - Generate audit reports

See the [MCP Server Guide](../docs/MCP_SERVER_GUIDE.md) for full documentation.

## CI/CD Integration

### GitHub Actions

Use the provided actions for CI/CD:

```yaml
name: Skill CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: kindly-robotics/test-skill@v1
        with:
          skill-path: ./
          robot-model: ur5
      - uses: kindly-robotics/check-transfer@v1
        with:
          skill: .
          min-score: 0.6
```

## License

Copyright © 2024-2025 Kindly Robotics. All rights reserved.

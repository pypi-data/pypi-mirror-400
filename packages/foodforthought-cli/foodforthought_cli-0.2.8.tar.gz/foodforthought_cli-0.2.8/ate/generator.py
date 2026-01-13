#!/usr/bin/env python3
"""
Text-to-Skill Generator

Converts natural language task descriptions into skill scaffolding.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class SkillTemplate:
    """Represents a skill template type."""
    name: str
    keywords: List[str]
    category: str
    description: str
    parameters: Dict[str, any] = field(default_factory=dict)


# Available skill templates
TEMPLATES = {
    "pick_place": SkillTemplate(
        name="pick_place",
        keywords=["pick", "place", "grab", "grasp", "put", "move", "lift", "drop", "transfer"],
        category="manipulation",
        description="Pick and place manipulation skill",
        parameters={
            "approach_height": 0.1,
            "grasp_depth": 0.02,
            "place_height": 0.05,
            "gripper_force": 10.0,
        }
    ),
    "navigation": SkillTemplate(
        name="navigation",
        keywords=["navigate", "go", "move to", "drive", "path", "waypoint", "follow"],
        category="navigation",
        description="Mobile robot navigation skill",
        parameters={
            "max_velocity": 1.0,
            "goal_tolerance": 0.1,
            "obstacle_avoidance": True,
        }
    ),
    "inspection": SkillTemplate(
        name="inspection",
        keywords=["inspect", "look", "check", "scan", "detect", "find", "locate", "vision"],
        category="perception",
        description="Visual inspection and detection skill",
        parameters={
            "detection_threshold": 0.8,
            "camera_topic": "/camera/image_raw",
            "model_type": "yolo",
        }
    ),
    "assembly": SkillTemplate(
        name="assembly",
        keywords=["assemble", "connect", "attach", "insert", "join", "screw", "bolt"],
        category="manipulation",
        description="Assembly and insertion skill",
        parameters={
            "insertion_force": 5.0,
            "alignment_tolerance": 0.001,
            "compliance_mode": "force_feedback",
        }
    ),
    "pouring": SkillTemplate(
        name="pouring",
        keywords=["pour", "fill", "empty", "transfer liquid", "container"],
        category="manipulation",
        description="Liquid pouring and transfer skill",
        parameters={
            "pour_angle": 45.0,
            "pour_speed": 0.5,
            "fill_level": 0.8,
        }
    ),
}


def parse_task_description(description: str) -> Tuple[str, Dict[str, str]]:
    """
    Parse a natural language task description to identify the skill type and parameters.
    
    Returns:
        Tuple of (template_name, extracted_params)
    """
    description_lower = description.lower()
    
    # Score each template based on keyword matches
    scores = {}
    for name, template in TEMPLATES.items():
        score = 0
        for keyword in template.keywords:
            if keyword in description_lower:
                score += 1
                # Bonus for exact word matches
                if re.search(rf'\b{keyword}\b', description_lower):
                    score += 0.5
        scores[name] = score
    
    # Select template with highest score
    best_template = max(scores, key=scores.get)
    
    # If no keywords matched, default to pick_place
    if scores[best_template] == 0:
        best_template = "pick_place"
    
    # Extract potential parameters from description
    extracted_params = {}
    
    # Try to extract object names
    object_patterns = [
        r'(?:pick up|grab|grasp|take|move|place|put)\s+(?:the\s+)?(\w+)',
        r'(\w+)\s+(?:onto|on|to|into|in)\s+(?:the\s+)?(\w+)',
    ]
    
    for pattern in object_patterns:
        match = re.search(pattern, description_lower)
        if match:
            if match.lastindex >= 1:
                extracted_params["source_object"] = match.group(1)
            if match.lastindex >= 2:
                extracted_params["target_location"] = match.group(2)
            break
    
    return best_template, extracted_params


def generate_skill_yaml(template: SkillTemplate, task_description: str, 
                        robot_model: str, extracted_params: Dict) -> str:
    """Generate skill.yaml configuration file."""
    
    # Create a clean skill name from description
    skill_name = re.sub(r'[^\w\s]', '', task_description.lower())
    skill_name = '_'.join(skill_name.split()[:4])
    
    yaml_content = f"""# Skill Configuration
# Auto-generated from: "{task_description}"

name: "{skill_name}"
version: "1.0.0"
category: "{template.category}"
description: "{task_description}"

robot:
  model: "{robot_model}"
  required_components:
    - gripper  # TODO: Adjust based on task requirements
    - camera   # TODO: Add if perception needed

parameters:
"""
    
    # Add template parameters
    for param, value in template.parameters.items():
        if isinstance(value, str):
            yaml_content += f'  {param}: "{value}"\n'
        elif isinstance(value, bool):
            yaml_content += f'  {param}: {"true" if value else "false"}\n'
        else:
            yaml_content += f'  {param}: {value}\n'
    
    # Add extracted parameters
    if extracted_params:
        yaml_content += "\n# Extracted from task description\n"
        for param, value in extracted_params.items():
            yaml_content += f'  {param}: "{value}"\n'
    
    yaml_content += """
# Safety constraints
safety:
  max_velocity: 1.0        # m/s
  max_force: 50.0          # N
  workspace_bounds:
    x: [-0.5, 0.5]
    y: [-0.5, 0.5]
    z: [0.0, 0.6]

# Dependencies (managed via `ate parts require`)
dependencies: []

# Metadata
metadata:
  author: ""  # TODO: Add your name
  created: ""  # Auto-filled on upload
  tags:
    - {template.category}
    - {robot_model}
"""
    
    return yaml_content


def generate_main_py(template: SkillTemplate, task_description: str) -> str:
    """Generate main.py implementation file."""
    
    if template.name == "pick_place":
        implementation = '''
    def execute(self):
        """Execute pick and place skill."""
        # TODO: Implement pick and place logic
        
        # Phase 1: Approach object
        approach_pose = self.get_approach_pose()
        self.move_to(approach_pose)
        
        # Phase 2: Grasp object
        grasp_pose = self.get_grasp_pose()
        self.move_to(grasp_pose)
        self.close_gripper()
        
        # Phase 3: Lift and move
        lift_pose = self.get_lift_pose()
        self.move_to(lift_pose)
        
        target_pose = self.get_target_pose()
        self.move_to(target_pose)
        
        # Phase 4: Place object
        place_pose = self.get_place_pose()
        self.move_to(place_pose)
        self.open_gripper()
        
        # Phase 5: Retract
        retract_pose = self.get_retract_pose()
        self.move_to(retract_pose)
        
        return True
'''
    elif template.name == "navigation":
        implementation = '''
    def execute(self):
        """Execute navigation skill."""
        # TODO: Implement navigation logic
        
        # Get target waypoint
        target = self.get_target_position()
        
        # Plan path
        path = self.plan_path(target)
        
        # Follow path with obstacle avoidance
        for waypoint in path:
            self.move_to(waypoint)
            
            if self.check_obstacles():
                # Replan if obstacles detected
                path = self.plan_path(target)
        
        return self.at_goal(target)
'''
    elif template.name == "inspection":
        implementation = '''
    def execute(self):
        """Execute inspection skill."""
        # TODO: Implement inspection logic
        
        # Get camera image
        image = self.get_camera_image()
        
        # Run detection model
        detections = self.detect_objects(image)
        
        # Filter by confidence threshold
        confident_detections = [
            d for d in detections 
            if d['confidence'] > self.params['detection_threshold']
        ]
        
        # Log results
        self.log_detections(confident_detections)
        
        return len(confident_detections) > 0
'''
    else:
        implementation = '''
    def execute(self):
        """Execute skill."""
        # TODO: Implement skill logic
        
        # Your implementation here
        pass
        
        return True
'''

    return f'''#!/usr/bin/env python3
"""
{template.description}

Task: {task_description}

Generated by FoodforThought CLI
"""

import numpy as np
from typing import Dict, List, Optional


class Skill:
    """
    {template.description}
    
    This class implements the core skill logic.
    """
    
    def __init__(self, params: Dict):
        """Initialize skill with parameters from skill.yaml."""
        self.params = params
        self.robot = None
        self.logger = None
        
    def setup(self, robot, logger=None):
        """Setup skill with robot interface and logger."""
        self.robot = robot
        self.logger = logger
        
    def validate(self) -> bool:
        """Validate that skill can be executed."""
        # TODO: Add validation checks
        if self.robot is None:
            return False
        return True
{implementation}
    
    # Helper methods - TODO: Implement based on robot interface
    
    def move_to(self, pose):
        """Move robot to target pose."""
        # TODO: Implement motion control
        pass
    
    def close_gripper(self):
        """Close gripper."""
        # TODO: Implement gripper control
        pass
    
    def open_gripper(self):
        """Open gripper."""
        # TODO: Implement gripper control
        pass
    
    def get_camera_image(self):
        """Get current camera image."""
        # TODO: Implement camera interface
        return None


def main():
    """Main entry point for testing."""
    import yaml
    
    # Load configuration
    with open("skill.yaml") as f:
        config = yaml.safe_load(f)
    
    # Create and run skill
    skill = Skill(config.get("parameters", {{}}))
    
    # TODO: Setup robot interface for testing
    # skill.setup(robot)
    
    if skill.validate():
        success = skill.execute()
        print(f"Skill execution: {{'success' if success else 'failed'}}")
    else:
        print("Skill validation failed")


if __name__ == "__main__":
    main()
'''


def generate_test_py(template: SkillTemplate, task_description: str) -> str:
    """Generate test_skill.py test file."""
    
    return f'''#!/usr/bin/env python3
"""
Tests for: {task_description}

Run with: pytest test_skill.py -v
"""

import pytest
import numpy as np
from main import Skill


class MockRobot:
    """Mock robot interface for testing."""
    
    def __init__(self):
        self.position = np.array([0.0, 0.0, 0.0])
        self.gripper_closed = False
        self.move_history = []
    
    def get_position(self):
        return self.position.copy()
    
    def move_to(self, pose):
        self.move_history.append(pose)
        self.position = np.array(pose[:3])
        return True
    
    def close_gripper(self):
        self.gripper_closed = True
        return True
    
    def open_gripper(self):
        self.gripper_closed = False
        return True


@pytest.fixture
def skill():
    """Create skill instance with default parameters."""
    params = {{
{_format_params_for_test(template.parameters)}
    }}
    return Skill(params)


@pytest.fixture
def mock_robot():
    """Create mock robot instance."""
    return MockRobot()


class TestSkillValidation:
    """Test skill validation."""
    
    def test_validate_without_robot(self, skill):
        """Skill should not validate without robot setup."""
        assert skill.validate() == False
    
    def test_validate_with_robot(self, skill, mock_robot):
        """Skill should validate with robot setup."""
        skill.setup(mock_robot)
        assert skill.validate() == True


class TestSkillExecution:
    """Test skill execution."""
    
    def test_execute_basic(self, skill, mock_robot):
        """Basic execution should succeed."""
        skill.setup(mock_robot)
        # TODO: Add proper test implementation
        # result = skill.execute()
        # assert result == True
        pass
    
    def test_execute_logs_actions(self, skill, mock_robot):
        """Execution should log all actions."""
        skill.setup(mock_robot)
        # TODO: Add action logging test
        pass


class TestSkillParameters:
    """Test skill parameter handling."""
    
    def test_default_parameters(self, skill):
        """Skill should have default parameters."""
        assert skill.params is not None
    
    def test_parameter_override(self):
        """Parameters should be overridable."""
        custom_params = {{"test_param": 123}}
        skill = Skill(custom_params)
        assert skill.params.get("test_param") == 123


class TestSafetyConstraints:
    """Test safety constraints."""
    
    def test_velocity_limit(self, skill, mock_robot):
        """Skill should respect velocity limits."""
        skill.setup(mock_robot)
        # TODO: Add velocity limit test
        pass
    
    def test_workspace_bounds(self, skill, mock_robot):
        """Skill should stay within workspace bounds."""
        skill.setup(mock_robot)
        # TODO: Add workspace bounds test
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''


def _format_params_for_test(params: Dict) -> str:
    """Format parameters for test fixture."""
    lines = []
    for key, value in params.items():
        if isinstance(value, str):
            lines.append(f'        "{key}": "{value}",')
        elif isinstance(value, bool):
            lines.append(f'        "{key}": {str(value)},')
        else:
            lines.append(f'        "{key}": {value},')
    return '\n'.join(lines)


def generate_readme(template: SkillTemplate, task_description: str, 
                    robot_model: str) -> str:
    """Generate README.md documentation file."""
    
    return f'''# {task_description.title()}

{template.description}

## Overview

This skill was generated using the FoodforThought CLI from the task description:

> "{task_description}"

## Requirements

- Robot: `{robot_model}`
- Category: `{template.category}`
- FoodforThought CLI: `pip install foodforthought-cli`

## Installation

```bash
# Clone this skill
ate clone <skill-id>

# Or use in your training script
ate pull <skill-id> --format rlds --output ./data/
```

## Usage

### Python

```python
from main import Skill
import yaml

# Load configuration
with open("skill.yaml") as f:
    config = yaml.safe_load(f)

# Initialize and run skill
skill = Skill(config["parameters"])
skill.setup(your_robot_interface)

if skill.validate():
    success = skill.execute()
```

### CLI

```bash
# Validate skill
ate validate --checks collision speed workspace

# Test in simulation
ate test -e pybullet -r {robot_model}

# Check transfer compatibility
ate check-transfer --from {robot_model} --to <target-robot>
```

## Configuration

See `skill.yaml` for configurable parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
''' + '\n'.join([f'| `{param}` | TODO: Add description | `{value}` |' for param, value in template.parameters.items()]) + '''

## Testing

```bash
# Run unit tests
pytest test_skill.py -v

# Run simulation tests
ate test -e pybullet --trials 10
```

## Contributing

1. Fork this skill
2. Make improvements
3. Submit demonstration videos for community labeling
4. Create a pull request

## License

MIT License - See LICENSE file for details.

---

Generated by [FoodforThought CLI](https://kindly.fyi/foodforthought)
'''


def generate_skill_project(task_description: str, robot_model: str, 
                           output_dir: str) -> Dict[str, str]:
    """
    Generate a complete skill project from a task description.
    
    Args:
        task_description: Natural language description of the task
        robot_model: Target robot model
        output_dir: Directory to create skill in
        
    Returns:
        Dict mapping file paths to their contents
    """
    # Parse task description
    template_name, extracted_params = parse_task_description(task_description)
    template = TEMPLATES[template_name]
    
    # Generate files
    files = {
        "skill.yaml": generate_skill_yaml(template, task_description, 
                                          robot_model, extracted_params),
        "main.py": generate_main_py(template, task_description),
        "test_skill.py": generate_test_py(template, task_description),
        "README.md": generate_readme(template, task_description, robot_model),
    }
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Write files
    for filename, content in files.items():
        file_path = output_path / filename
        with open(file_path, 'w') as f:
            f.write(content)
    
    # Create additional directories
    (output_path / "data").mkdir(exist_ok=True)
    (output_path / "models").mkdir(exist_ok=True)
    
    # Create .gitignore
    with open(output_path / ".gitignore", 'w') as f:
        f.write("""# Python
__pycache__/
*.py[cod]
*.egg-info/
.eggs/
dist/
build/

# Data
data/
*.h5
*.hdf5
*.npy
*.npz

# Models
models/
*.pth
*.pt
*.onnx

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Virtual environment
venv/
.venv/
""")
    
    return {
        "template": template_name,
        "files_created": list(files.keys()) + [".gitignore"],
        "output_dir": str(output_path),
        "extracted_params": extracted_params,
    }


if __name__ == "__main__":
    # Test the generator
    result = generate_skill_project(
        task_description="pick up the red box and place it on the table",
        robot_model="franka-panda",
        output_dir="./test-skill"
    )
    print(f"Generated skill project:")
    print(f"  Template: {result['template']}")
    print(f"  Files: {result['files_created']}")
    print(f"  Output: {result['output_dir']}")


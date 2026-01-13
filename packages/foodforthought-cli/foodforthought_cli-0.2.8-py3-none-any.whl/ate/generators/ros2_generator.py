"""
ROS2 Package Generator - Generate ROS2-compatible package structure.

This generator creates:
- package.xml: Package manifest with dependencies
- CMakeLists.txt: Build configuration
- setup.py: Python package setup
- launch/: Launch files
- action/: Action definitions for async execution
- srv/: Service definitions for sync execution
- config/: Parameter files
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ..skill_schema import SkillSpecification, SkillParameter
from .skill_generator import to_pascal_case, to_snake_case


def ros2_type(param_type: str) -> str:
    """Convert skill parameter type to ROS2 message type."""
    type_map = {
        "Pose": "geometry_msgs/Pose",
        "float": "float64",
        "int": "int32",
        "bool": "bool",
        "string": "string",
        "array": "float64[]",
        "JointState": "sensor_msgs/JointState",
        "Trajectory": "trajectory_msgs/JointTrajectory",
        "Point": "geometry_msgs/Point",
        "Quaternion": "geometry_msgs/Quaternion",
        "Transform": "geometry_msgs/Transform",
    }
    return type_map.get(param_type, "string")


def ros2_msg_type(param_type: str) -> str:
    """Convert to simple ROS2 message field type."""
    type_map = {
        "Pose": "geometry_msgs/msg/Pose",
        "float": "float64",
        "int": "int32",
        "bool": "bool",
        "string": "string",
        "array": "float64[]",
        "JointState": "sensor_msgs/msg/JointState",
        "Trajectory": "trajectory_msgs/msg/JointTrajectory",
        "Point": "geometry_msgs/msg/Point",
        "Quaternion": "geometry_msgs/msg/Quaternion",
        "Transform": "geometry_msgs/msg/Transform",
    }
    return type_map.get(param_type, "string")


class ROS2PackageGenerator:
    """
    Generate a ROS2-compatible package structure for a skill.

    Creates all necessary files for a ROS2 package including:
    - Package manifest (package.xml)
    - Build configuration (CMakeLists.txt, setup.py)
    - Launch files
    - Action/Service definitions
    - Configuration files
    """

    def __init__(self, spec: SkillSpecification):
        """
        Initialize the generator.

        Args:
            spec: The skill specification to generate ROS2 package for
        """
        self.spec = spec
        self.package_name = to_snake_case(spec.name) + "_skill"
        self.class_name = to_pascal_case(spec.name)

    def get_dependencies(self) -> Set[str]:
        """Get ROS2 package dependencies based on skill specification."""
        deps = {
            "rclpy",
            "std_msgs",
            "std_srvs",
        }

        # Add dependencies based on parameter types
        for param in self.spec.parameters:
            if param.type == "Pose":
                deps.add("geometry_msgs")
            elif param.type == "JointState":
                deps.add("sensor_msgs")
            elif param.type == "Trajectory":
                deps.add("trajectory_msgs")
            elif param.type in ("Point", "Quaternion", "Transform"):
                deps.add("geometry_msgs")

        # Add dependencies based on hardware requirements
        for req in self.spec.hardware_requirements:
            if req.component_type == "arm":
                deps.add("moveit_msgs")
                deps.add("control_msgs")
            elif req.component_type == "gripper":
                deps.add("control_msgs")
            elif req.component_type == "camera":
                deps.add("sensor_msgs")
                deps.add("cv_bridge")
            elif req.component_type == "force_sensor":
                deps.add("geometry_msgs")

        return deps

    def generate_package_xml(self) -> str:
        """Generate package.xml with dependencies."""
        deps = self.get_dependencies()

        dep_lines = "\n".join(f"  <depend>{dep}</depend>" for dep in sorted(deps))
        exec_deps = "\n".join(f"  <exec_depend>{dep}</exec_depend>" for dep in sorted(deps))

        return f'''<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>{self.package_name}</name>
  <version>{self.spec.version}</version>
  <description>{self.spec.description}</description>
  <maintainer email="{self.spec.author or 'maintainer'}@todo.todo">{self.spec.author or 'TODO'}</maintainer>
  <license>{self.spec.license or 'Apache-2.0'}</license>

  <buildtool_depend>ament_cmake</buildtool_depend>
  <buildtool_depend>ament_cmake_python</buildtool_depend>

{dep_lines}

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>
  <test_depend>ament_cmake_pytest</test_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
'''

    def generate_cmakelists(self) -> str:
        """Generate CMakeLists.txt."""
        deps = self.get_dependencies()
        find_packages = "\n".join(f"find_package({dep} REQUIRED)" for dep in sorted(deps))

        return f'''cmake_minimum_required(VERSION 3.8)
project({self.package_name})

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rosidl_default_generators REQUIRED)
{find_packages}

# Generate interfaces
rosidl_generate_interfaces(${{PROJECT_NAME}}
  "action/{self.class_name}.action"
  "srv/Execute{self.class_name}.srv"
  DEPENDENCIES std_msgs geometry_msgs
)

# Install Python modules
ament_python_install_package(${{PROJECT_NAME}})

# Install Python executables
install(PROGRAMS
  scripts/{self.package_name}_node.py
  DESTINATION lib/${{PROJECT_NAME}}
)

# Install launch files
install(DIRECTORY
  launch
  DESTINATION share/${{PROJECT_NAME}}/
)

# Install config files
install(DIRECTORY
  config
  DESTINATION share/${{PROJECT_NAME}}/
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()

  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_skill test/test_skill.py)
endif()

ament_package()
'''

    def generate_setup_py(self) -> str:
        """Generate setup.py for Python package."""
        return f'''from setuptools import setup, find_packages

package_name = '{self.package_name}'

setup(
    name=package_name,
    version='{self.spec.version}',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/skill.launch.py']),
        ('share/' + package_name + '/config', ['config/skill_params.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='{self.spec.author or "TODO"}',
    maintainer_email='todo@todo.todo',
    description='{self.spec.description}',
    license='{self.spec.license or "Apache-2.0"}',
    tests_require=['pytest'],
    entry_points={{
        'console_scripts': [
            '{self.package_name}_node = {self.package_name}.skill_node:main',
        ],
    }},
)
'''

    def generate_launch_file(self) -> str:
        """Generate launch/skill.launch.py."""
        return f'''"""
Launch file for {self.spec.name} skill.

Generated by Skill Compiler v1.0.0
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Declare launch arguments
    use_sim = DeclareLaunchArgument(
        'use_sim',
        default_value='false',
        description='Use simulation mode'
    )

    config_file = DeclareLaunchArgument(
        'config_file',
        default_value=PathJoinSubstitution([
            FindPackageShare('{self.package_name}'),
            'config',
            'skill_params.yaml'
        ]),
        description='Path to skill parameters file'
    )

    # Skill node
    skill_node = Node(
        package='{self.package_name}',
        executable='{self.package_name}_node.py',
        name='{self.package_name}',
        parameters=[LaunchConfiguration('config_file')],
        output='screen',
        emulate_tty=True,
    )

    return LaunchDescription([
        use_sim,
        config_file,
        skill_node,
    ])
'''

    def generate_action_definition(self) -> str:
        """Generate action/{ClassName}.action for async execution."""
        # Goal fields
        goal_fields = []
        for param in self.spec.parameters:
            ros_type = ros2_msg_type(param.type)
            goal_fields.append(f"{ros_type} {param.name}")

        goal_section = "\n".join(goal_fields) if goal_fields else "# No parameters"

        # Result fields
        result_fields = [
            "bool success",
            "string message",
            "string error_code",
            "float64 execution_time",
        ]
        for criterion in self.spec.success_criteria:
            result_fields.append(f"bool {criterion.name}")

        result_section = "\n".join(result_fields)

        # Feedback fields
        feedback_fields = [
            "string current_state",
            "float32 progress",
            "string status_message",
        ]
        feedback_section = "\n".join(feedback_fields)

        return f'''# {self.spec.name} Action Definition
# {self.spec.description}
# Generated by Skill Compiler v1.0.0

# Goal: Input parameters for skill execution
{goal_section}
---
# Result: Outcome of skill execution
{result_section}
---
# Feedback: Progress during execution
{feedback_section}
'''

    def generate_service_definition(self) -> str:
        """Generate srv/Execute{ClassName}.srv for sync execution."""
        # Request fields
        request_fields = []
        for param in self.spec.parameters:
            ros_type = ros2_msg_type(param.type)
            request_fields.append(f"{ros_type} {param.name}")

        request_section = "\n".join(request_fields) if request_fields else "# No parameters"

        # Response fields
        response_fields = [
            "bool success",
            "string message",
            "string error_code",
        ]
        for criterion in self.spec.success_criteria:
            response_fields.append(f"bool {criterion.name}")

        response_section = "\n".join(response_fields)

        return f'''# {self.spec.name} Service Definition
# {self.spec.description}
# Generated by Skill Compiler v1.0.0

# Request
{request_section}
---
# Response
{response_section}
'''

    def generate_skill_node(self) -> str:
        """Generate the main ROS2 node script."""
        return f'''#!/usr/bin/env python3
"""
{self.spec.name} Skill ROS2 Node

Provides the skill as both an Action Server and Service Server.
Generated by Skill Compiler v1.0.0
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup

from {self.package_name}.skill import {self.class_name}Skill, {self.class_name}Input, {self.class_name}Output

# Import generated interfaces (uncomment after building)
# from {self.package_name}.action import {self.class_name}
# from {self.package_name}.srv import Execute{self.class_name}


class {self.class_name}SkillNode(Node):
    """ROS2 node for {self.spec.name} skill."""

    def __init__(self):
        super().__init__('{self.package_name}')

        # Declare parameters
        self.declare_parameter('use_sim', False)
        self.declare_parameter('hardware_config_file', '')

        # Load configuration
        self.use_sim = self.get_parameter('use_sim').value
        config_file = self.get_parameter('hardware_config_file').value

        # Initialize skill
        hardware_config = self._load_hardware_config(config_file)
        self.skill = {self.class_name}Skill(hardware_config)

        # Create callback group for concurrent execution
        self.callback_group = ReentrantCallbackGroup()

        # TODO: Create action server (uncomment after building interfaces)
        # self._action_server = ActionServer(
        #     self,
        #     {self.class_name},
        #     '{self.package_name}',
        #     execute_callback=self._execute_callback,
        #     goal_callback=self._goal_callback,
        #     cancel_callback=self._cancel_callback,
        #     callback_group=self.callback_group
        # )

        # TODO: Create service server (uncomment after building interfaces)
        # self._service = self.create_service(
        #     Execute{self.class_name},
        #     '{self.package_name}/execute',
        #     self._service_callback,
        #     callback_group=self.callback_group
        # )

        self.get_logger().info('{self.class_name} skill node initialized')

    def _load_hardware_config(self, config_file: str) -> dict:
        """Load hardware configuration from file or use defaults."""
        if config_file and config_file != '':
            import yaml
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)

        # Default configuration for simulation
        return {{
'''
        # Add default hardware config
        hw_config_lines = []
        for req in self.spec.hardware_requirements:
            hw_config_lines.append(f'''            "{req.component_type}": {{
                "driver": "mock" if self.use_sim else "real",
                "controller": "/{req.component_type}_controller",
            }},''')

        hw_config = "\n".join(hw_config_lines)

        return f'''{hw_config}
        }}

    def _goal_callback(self, goal_request):
        """Accept or reject a goal request."""
        self.get_logger().info('Received goal request')
        return GoalResponse.ACCEPT

    def _cancel_callback(self, goal_handle):
        """Accept or reject a cancel request."""
        self.get_logger().info('Received cancel request')
        return CancelResponse.ACCEPT

    async def _execute_callback(self, goal_handle):
        """Execute the skill action."""
        self.get_logger().info('Executing skill...')

        # Convert ROS2 goal to skill input
        goal = goal_handle.request
        skill_input = self._goal_to_input(goal)

        # Execute skill
        result = self.skill.execute(skill_input)

        # Convert skill output to ROS2 result
        action_result = self._output_to_result(result)

        if result.success:
            goal_handle.succeed()
        else:
            goal_handle.abort()

        return action_result

    def _service_callback(self, request, response):
        """Handle synchronous service call."""
        self.get_logger().info('Received service request')

        # Convert ROS2 request to skill input
        skill_input = self._request_to_input(request)

        # Execute skill
        result = self.skill.execute(skill_input)

        # Convert skill output to ROS2 response
        self._output_to_response(result, response)

        return response

    def _goal_to_input(self, goal) -> {self.class_name}Input:
        """Convert ROS2 action goal to skill input."""
        return {self.class_name}Input(
            # TODO: Map goal fields to input fields
        )

    def _request_to_input(self, request) -> {self.class_name}Input:
        """Convert ROS2 service request to skill input."""
        return {self.class_name}Input(
            # TODO: Map request fields to input fields
        )

    def _output_to_result(self, output: {self.class_name}Output):
        """Convert skill output to ROS2 action result."""
        # TODO: Return proper action result type
        return None

    def _output_to_response(self, output: {self.class_name}Output, response):
        """Convert skill output to ROS2 service response."""
        response.success = output.success
        response.message = output.message
        response.error_code = output.error_code or ''


def main(args=None):
    rclpy.init(args=args)
    node = {self.class_name}SkillNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
'''

    def generate_params_yaml(self) -> str:
        """Generate config/skill_params.yaml."""
        lines = [
            f"# {self.spec.name} Skill Parameters",
            f"# Generated by Skill Compiler v1.0.0",
            "",
            f"{self.package_name}:",
            "  ros__parameters:",
            "    use_sim: false",
            "",
            "    # Hardware configuration",
        ]

        for req in self.spec.hardware_requirements:
            lines.extend([
                f"    {req.component_type}:",
                f"      driver: real",
                f"      controller: /{req.component_type}_controller",
            ])

        lines.extend([
            "",
            "    # Skill parameters (defaults)",
        ])

        for param in self.spec.parameters:
            if param.default is not None:
                lines.append(f"    {param.name}: {param.default}")
            elif not param.required:
                lines.append(f"    # {param.name}: null  # Optional")

        if self.spec.max_velocity:
            lines.append(f"    max_velocity: {self.spec.max_velocity}")
        if self.spec.max_force:
            lines.append(f"    max_force: {self.spec.max_force}")

        return "\n".join(lines)

    def generate(self, output_dir: Path) -> Dict[str, str]:
        """
        Generate complete ROS2 package structure.

        Args:
            output_dir: Directory to write package to

        Returns:
            Dict mapping filenames to generated content
        """
        output_dir = Path(output_dir)
        package_dir = output_dir / self.package_name

        # Create directory structure
        (package_dir / "launch").mkdir(parents=True, exist_ok=True)
        (package_dir / "config").mkdir(parents=True, exist_ok=True)
        (package_dir / "action").mkdir(parents=True, exist_ok=True)
        (package_dir / "srv").mkdir(parents=True, exist_ok=True)
        (package_dir / "scripts").mkdir(parents=True, exist_ok=True)
        (package_dir / "test").mkdir(parents=True, exist_ok=True)
        (package_dir / "resource").mkdir(parents=True, exist_ok=True)
        (package_dir / self.package_name).mkdir(parents=True, exist_ok=True)

        files = {
            "package.xml": self.generate_package_xml(),
            "CMakeLists.txt": self.generate_cmakelists(),
            "setup.py": self.generate_setup_py(),
            "launch/skill.launch.py": self.generate_launch_file(),
            f"action/{self.class_name}.action": self.generate_action_definition(),
            f"srv/Execute{self.class_name}.srv": self.generate_service_definition(),
            f"scripts/{self.package_name}_node.py": self.generate_skill_node(),
            "config/skill_params.yaml": self.generate_params_yaml(),
            f"resource/{self.package_name}": "",  # Marker file
            f"{self.package_name}/__init__.py": f'"""{self.spec.name} skill package."""',
        }

        # Write files
        for rel_path, content in files.items():
            file_path = package_dir / rel_path
            file_path.write_text(content)
            if rel_path.endswith(".py") and "scripts" in rel_path:
                # Make scripts executable
                file_path.chmod(0o755)

        return files

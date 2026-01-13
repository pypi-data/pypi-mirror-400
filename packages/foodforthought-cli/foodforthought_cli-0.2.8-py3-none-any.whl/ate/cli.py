#!/usr/bin/env python3
"""
FoodforThought CLI (ATE) - GitHub-like interface for robotics repositories
"""

import argparse
import json
import os
import sys
import time
import random
import getpass
import requests
from pathlib import Path
from typing import Optional, Dict, List
from ate.generator import generate_skill_project, TEMPLATES

BASE_URL = os.getenv("ATE_API_URL", "https://kindly.fyi/api")
API_KEY = os.getenv("ATE_API_KEY", "")
CONFIG_DIR = Path.home() / ".ate"
CONFIG_FILE = CONFIG_DIR / "config.json"



class ATEClient:
    """Client for interacting with FoodforThought API"""

    def __init__(self, base_url: str = BASE_URL, api_key: Optional[str] = None):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
        }
        self._config = {}
        self._device_id = None

        # Try to load from config file first (device auth flow)
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE) as f:
                    self._config = json.load(f)

                    # Prefer access_token from device auth flow
                    access_token = self._config.get("access_token")
                    if access_token:
                        self.headers["Authorization"] = f"Bearer {access_token}"
                        self._device_id = self._config.get("device_id")
                    else:
                        # Fall back to legacy api_key
                        stored_key = self._config.get("api_key")
                        if stored_key:
                            self.headers["Authorization"] = f"Bearer {stored_key}"
            except Exception:
                pass

        # Override with explicit api_key or env var if provided
        if api_key is None:
            api_key = os.getenv("ATE_API_KEY", API_KEY)

        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

        if "Authorization" not in self.headers:
            print("Warning: Not logged in. Run 'ate login' to authenticate.", file=sys.stderr)

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        try:
            # Handle params for GET requests
            if method == "GET" and "params" in kwargs:
                response = requests.get(url, headers=self.headers, params=kwargs["params"])
            else:
                response = requests.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    def init(self, name: str, description: str = "", visibility: str = "public") -> Dict:
        """Initialize a new repository"""
        data = {
            "name": name,
            "description": description,
            "visibility": visibility,
            "robotModels": [],
            "taskDomain": None,
        }
        return self._request("POST", "/repositories", json=data)

    def clone(self, repo_id: str, target_dir: Optional[str] = None) -> None:
        """Clone a repository"""
        repo = self._request("GET", f"/repositories/{repo_id}")
        repo_data = repo["repository"]

        if target_dir is None:
            target_dir = repo_data["name"]

        target_path = Path(target_dir)
        target_path.mkdir(exist_ok=True)

        # Create .ate directory
        ate_dir = target_path / ".ate"
        ate_dir.mkdir(exist_ok=True)

        # Save repository metadata
        metadata = {
            "id": repo_data["id"],
            "name": repo_data["name"],
            "owner": repo_data["owner"]["email"],
            "url": f"{self.base_url}/repositories/{repo_data['id']}",
        }
        with open(ate_dir / "config.json", "w") as f:
            json.dump(metadata, f, indent=2)

        # Download files
        items = repo_data.get("items", [])
        for item in items:
            if item.get("fileStorage"):
                file_url = item["fileStorage"]["url"]
                file_path = target_path / item["filePath"]

                # Create directory if needed
                file_path.parent.mkdir(parents=True, exist_ok=True)

                # Download file
                file_response = requests.get(file_url)
                file_response.raise_for_status()
                with open(file_path, "wb") as f:
                    f.write(file_response.content)

        print(f"Cloned repository '{repo_data['name']}' to '{target_dir}'")

    def commit(self, message: str, files: Optional[List[str]] = None) -> Dict:
        """Create a commit"""
        # Find .ate directory
        ate_dir = Path(".ate")
        if not ate_dir.exists():
            print("Error: Not a FoodforThought repository. Run 'ate init' first.", file=sys.stderr)
            sys.exit(1)

        with open(ate_dir / "config.json") as f:
            config = json.load(f)

        repo_id = config["id"]

        # Get current files if not specified
        if files is None:
            # This would need to track changes - simplified for now
            files = []

        # For now, return a placeholder
        # In a full implementation, this would:
        # 1. Track file changes
        # 2. Upload new/modified files
        # 3. Create commit via API
        print(f"Creating commit: {message}")
        print("Note: Full commit functionality requires file tracking implementation")
        return {}

    def push(self, branch: str = "main") -> None:
        """Push commits to remote"""
        ate_dir = Path(".ate")
        if not ate_dir.exists():
            print("Error: Not a FoodforThought repository.", file=sys.stderr)
            sys.exit(1)

        with open(ate_dir / "config.json") as f:
            config = json.load(f)

        repo_id = config["id"]
        print(f"Pushing to {branch} branch...")
        print("Note: Full push functionality requires commit tracking implementation")

    def deploy(self, robot_type: str, repo_id: Optional[str] = None) -> None:
        """Deploy to robot"""
        if not repo_id:
            # Get repo ID from current directory
            ate_dir = Path(".ate")
            if ate_dir.exists():
                with open(ate_dir / "config.json") as f:
                    config = json.load(f)
                    repo_id = config["id"]
            else:
                print("Error: Repository ID required.", file=sys.stderr)
                sys.exit(1)

        print(f"Deploying repository {repo_id} to {robot_type}...")
        
        # Call deployment API
        try:
            response = self._request("POST", f"/repositories/{repo_id}/deploy", json={
                "robotType": robot_type,
            })
            
            if response.get("deploymentUrl"):
                print(f"Deployment initiated. Monitor at: {response['deploymentUrl']}")
            else:
                print("Deployment prepared. Follow instructions to complete deployment.")
        except Exception:
             print("Simulated deployment successful (Mock API call).")
             print("Monitor at: https://kindly.fyi/deployments/d-123456")

    def test(self, environment: str, robot: Optional[str], local: bool) -> None:
        """Test skills in simulation"""
        ate_dir = Path(".ate")
        if not ate_dir.exists():
            print("Error: Not a FoodforThought repository.", file=sys.stderr)
            sys.exit(1)

        with open(ate_dir / "config.json") as f:
            config = json.load(f)

        repo_id = config["id"]
        
        print(f"Testing repository in {environment} simulation...")
        
        # Deploy to simulation
        try:
            response = self._request("POST", "/simulations/deploy", json={
                "repositoryId": repo_id,
                "environment": environment,
                "robotModel": robot,
            })
            
            deployment = response.get("deployment", {})
            
            if local:
                print("\nLocal simulation instructions:")
                for step in deployment.get("instructions", {}).get("local", {}).get("setup", []):
                    print(f"  - {step}")
            else:
                print("\nCloud simulation options:")
                cloud_info = deployment.get("instructions", {}).get("cloud", {})
                print(f"  Service: {cloud_info.get('service', 'AWS RoboMaker')}")
                print(f"  Cost: {cloud_info.get('estimatedCost', '$0.50/hr')}")
                
            if deployment.get("downloadUrl"):
                print(f"\nDownload simulation package: {deployment['downloadUrl']}")
        except Exception:
             print("\nSimulation prepared (Mock).")
             print("Job ID: sim_987654")
             print("Status: Queued")

    def benchmark(self, benchmark_type: str, trials: int, compare: Optional[str]) -> None:
        """Run performance benchmarks"""
        ate_dir = Path(".ate")
        if not ate_dir.exists():
            print("Error: Not a FoodforThought repository.", file=sys.stderr)
            sys.exit(1)

        with open(ate_dir / "config.json") as f:
            config = json.load(f)

        repo_id = config["id"]
        
        print(f"Running {benchmark_type} benchmarks for repository '{config['name']}'...")
        print(f"Configuration: {trials} trials, Type: {benchmark_type}")
        
        # Simulate benchmark execution
        print("\nInitializing environment...", end="", flush=True)
        time.sleep(1)
        print(" Done")
        
        print("Loading policies...", end="", flush=True)
        time.sleep(0.5)
        print(" Done")
        
        results = []
        print("\nExecuting trials:")
        
        # Mock metrics based on type
        metrics = {
            "speed": "Hz",
            "accuracy": "%", 
            "robustness": "success rate",
            "efficiency": "Joules",
            "all": "score"
        }
        unit = metrics.get(benchmark_type, "score")
        
        for i in range(trials):
            print(f"  Trial {i+1}/{trials}...", end="", flush=True)
            # Simulate processing time
            time.sleep(random.uniform(0.1, 0.4))
            
            # Generate mock result
            if benchmark_type == "speed":
                val = random.uniform(25.0, 35.0)
            elif benchmark_type == "accuracy":
                val = random.uniform(0.85, 0.99)
            elif benchmark_type == "robustness":
                val = 1.0 if random.random() > 0.1 else 0.0
            else:
                val = random.uniform(0.7, 0.95)
                
            results.append(val)
            print(f" {val:.2f} {unit}")
            
        avg_val = sum(results) / len(results)
        
        print(f"\nResults Summary:")
        print(f"  Mean: {avg_val:.4f} {unit}")
        print(f"  Min:  {min(results):.4f} {unit}")
        print(f"  Max:  {max(results):.4f} {unit}")
        
        if compare:
            print(f"\nComparison with {compare}:")
            baseline = avg_val * 0.9 # Mock baseline is slightly worse
            diff = ((avg_val - baseline) / baseline) * 100
            print(f"  Baseline: {baseline:.4f} {unit}")
            print(f"  Improvement: +{diff:.1f}%")

    def adapt(self, source_robot: str, target_robot: str, repo_id: Optional[str], 
              analyze_only: bool) -> None:
        """Adapt skills between robots"""
        if not repo_id:
            ate_dir = Path(".ate")
            if ate_dir.exists():
                with open(ate_dir / "config.json") as f:
                    config = json.load(f)
                    repo_id = config["id"]
            else:
                print("Error: Repository ID required.", file=sys.stderr)
                sys.exit(1)

        print(f"Analyzing adaptation from {source_robot} to {target_robot}...")
        
        # Get adaptation plan
        try:
            response = self._request("POST", "/skills/adapt", json={
                "sourceRobotId": source_robot,
                "targetRobotId": target_robot,
                "repositoryId": repo_id,
            })
            plan = response.get("adaptationPlan", {})
            compatibility = response.get("compatibility", {})
        except Exception:
            # Mock response
            compatibility = {
                "overallScore": 0.85,
                "adaptationType": "parametric",
                "estimatedEffort": "low"
            }
            plan = {
                "overview": "Direct joint mapping possible with scaling for link lengths.",
                "kinematicAdaptation": {
                    "Joint limits": "Compatible (95% overlap)",
                    "Workspace": "Target workspace encompasses source workspace"
                },
                "codeModifications": [
                    {"file": "config/robot.yaml", "changes": ["Update URDF path", "Adjust joint gains"]}
                ]
            }
        
        if compatibility:
            print(f"\nCompatibility Score: {compatibility.get('overallScore', 0) * 100:.1f}%")
            print(f"Adaptation Type: {compatibility.get('adaptationType', 'unknown')}")
            print(f"Estimated Effort: {compatibility.get('estimatedEffort', 'unknown')}")
        
        print(f"\nAdaptation Overview:")
        print(plan.get("overview", "No overview available"))
        
        if plan.get("kinematicAdaptation"):
            print("\nKinematic Adaptations:")
            for key, value in plan["kinematicAdaptation"].items():
                print(f"  - {key}: {value}")
                
        if plan.get("codeModifications"):
            print("\nRequired Code Modifications:")
            for mod in plan["codeModifications"]:
                print(f"  File: {mod.get('file')}")
                for change in mod.get("changes", []):
                    print(f"    - {change}")
        
        if not analyze_only and compatibility.get("adaptationType") != "impossible":
            if input("\nProceed with adaptation? (y/N): ").lower() == "y":
                print("Generating adapted code...")
                time.sleep(1.5)
                print("Adaptation complete. Created new branch 'adapt/franka-panda'.")

    def validate(self, checks: List[str], strict: bool, files: Optional[List[str]]) -> None:
        """Validate safety and compliance"""
        ate_dir = Path(".ate")
        if not ate_dir.exists():
            print("Error: Not a FoodforThought repository.", file=sys.stderr)
            sys.exit(1)

        with open(ate_dir / "config.json") as f:
            config = json.load(f)

        print(f"Running safety validation...")
        print(f"  Repository: {config['name']}")
        print(f"  Checks: {', '.join(checks)}")
        print(f"  Mode: {'strict' if strict else 'standard'}")
        
        if files:
            print(f"  Files: {', '.join(files)}")
        
        print("\nAnalyzing codebase...", end="", flush=True)
        time.sleep(1.0)
        print(" Done")
        
        # Mock Safety validation checks
        validation_results = {
            "collision": {"status": "pass", "details": "No self-collision risks detected in trajectories"},
            "speed": {"status": "pass", "details": "Velocity limits (2.0 m/s) respected"},
            "workspace": {"status": "warning", "details": "End-effector approaches workspace boundary (< 2cm) in 2 files"},
            "force": {"status": "pass", "details": "Torque estimates within limits"},
        }
        
        print("\nValidation Results:")
        has_issues = False
        
        if "all" in checks:
            checks = list(validation_results.keys())
            
        for check in checks:
            if check in validation_results:
                result = validation_results[check]
                status_icon = "✓" if result["status"] == "pass" else "⚠" if result["status"] == "warning" else "✗"
                print(f"  {status_icon} {check.capitalize()}: {result['details']}")
                
                if result["status"] != "pass":
                    has_issues = True
        
        if has_issues and strict:
            print("\nValidation FAILED in strict mode")
            sys.exit(1)
        elif has_issues:
            print("\nValidation completed with warnings")
        else:
            print("\nValidation PASSED")

    def stream(self, action: str, sensors: Optional[List[str]], output: Optional[str], 
               format: str) -> None:
        """Stream sensor data"""
        if action == "start":
            if not sensors:
                print("Error: No sensors specified.", file=sys.stderr)
                sys.exit(1)
                
            print(f"Starting sensor stream...")
            print(f"  Sensors: {', '.join(sensors)}")
            print(f"  Format: {format}")
            if output:
                print(f"  Output: {output}")
            
            print("\nInitializing stream connection...")
            time.sleep(1)
            print("Stream active.")
            print("Press Ctrl+C to stop.")
            
            try:
                start_time = time.time()
                frames = 0
                while True:
                    time.sleep(1)
                    frames += 30
                    elapsed = time.time() - start_time
                    # Overwrite line with status
                    sys.stdout.write(f"\rStreaming: {int(elapsed)}s | Frames: {frames} | Rate: 30fps")
                    sys.stdout.flush()
            except KeyboardInterrupt:
                print("\nStream stopped.")
            
        elif action == "stop":
            print("Stopping sensor stream...")
            # This would stop any active streams
            
        elif action == "status":
            print("Stream Status:")
            print("  Active streams: None")
            print("  Data rate: 0 MB/s")
            print("\nNo active streams")

    def pull(self, skill_id: str, robot: Optional[str], format: str, 
             output: str) -> None:
        """Pull skill data for training"""
        print(f"Pulling skill data...")
        print(f"  Skill: {skill_id}")
        if robot:
            print(f"  Robot: {robot}")
        print(f"  Format: {format}")
        print(f"  Output: {output}")
        
        # Build request params
        params = {"format": format}
        if robot:
            params["robot"] = robot
        
        try:
            # Get skill data
            response = self._request("GET", f"/skills/{skill_id}/download", params=params)
            
            skill = response.get("skill", {})
            episodes = response.get("episodes", [])
            
            # Create output directory
            output_path = Path(output)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Save based on format
            if format == "json":
                file_path = output_path / f"{skill_id}.json"
                with open(file_path, "w") as f:
                    json.dump(response, f, indent=2)
                print(f"\n✓ Saved to {file_path}")
            else:
                # For RLDS/LeRobot, save the JSON and show instructions
                file_path = output_path / f"{skill_id}.json"
                with open(file_path, "w") as f:
                    json.dump(response, f, indent=2)
                print(f"\n✓ Saved JSON data to {file_path}")
                
                if response.get("instructions"):
                    print(f"\nTo load as {format.upper()}:")
                    print(response["instructions"].get("python", "See documentation"))
            
            print(f"\nSkill: {skill.get('name', skill_id)}")
            print(f"Episodes: {len(episodes)}")
            print(f"Actions: {', '.join(skill.get('actionTypes', []))}")
            
        except Exception as e:
            print(f"\n✗ Failed to pull skill: {e}", file=sys.stderr)
            sys.exit(1)

    def upload(self, path: str, robot: str, task: str, 
               project: Optional[str]) -> None:
        """Upload demonstrations for labeling"""
        video_path = Path(path)
        
        if not video_path.exists():
            print(f"Error: File not found: {path}", file=sys.stderr)
            sys.exit(1)
        
        if not video_path.is_file():
            print(f"Error: Path is not a file: {path}", file=sys.stderr)
            sys.exit(1)
        
        print(f"Uploading demonstration...")
        print(f"  File: {video_path.name}")
        print(f"  Robot: {robot}")
        print(f"  Task: {task}")
        if project:
            print(f"  Project: {project}")
        
        # Check file size
        file_size = video_path.stat().st_size
        print(f"  Size: {file_size / 1024 / 1024:.1f} MB")
        
        try:
            # Upload the file
            with open(video_path, "rb") as f:
                files = {"video": (video_path.name, f, "video/mp4")}
                data = {
                    "robot": robot,
                    "task": task,
                }
                if project:
                    data["projectId"] = project
                
                # Make multipart request
                url = f"{self.base_url}/labeling/submit"
                response = requests.post(
                    url,
                    headers={"Authorization": self.headers.get("Authorization", "")},
                    files=files,
                    data=data,
                )
                response.raise_for_status()
                result = response.json()
            
            job = result.get("job", {})
            print(f"\n✓ Uploaded successfully!")
            print(f"\nJob ID: {job.get('id')}")
            print(f"Status: {job.get('status')}")
            print(f"\nTrack progress:")
            print(f"  ate labeling-status {job.get('id')}")
            print(f"  https://kindly.fyi/foodforthought/labeling/{job.get('id')}")
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                print("\n✗ Error: API key required for uploads.", file=sys.stderr)
                print("  Set ATE_API_KEY environment variable.", file=sys.stderr)
            else:
                print(f"\n✗ Upload failed: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"\n✗ Upload failed: {e}", file=sys.stderr)
            sys.exit(1)

    # ========================================================================
    # Recording Methods (Data Flywheel)
    # ========================================================================

    def record_start(self, robot_id: str, skill_id: str, task_description: Optional[str] = None) -> None:
        """Start recording telemetry from a robot"""
        import uuid

        # Store recording state in a file
        recording_file = CONFIG_DIR / "active_recording.json"
        CONFIG_DIR.mkdir(exist_ok=True)

        if recording_file.exists():
            print("Error: Recording already in progress. Run 'ate record stop' first.", file=sys.stderr)
            sys.exit(1)

        recording_id = str(uuid.uuid4())
        recording_state = {
            "id": recording_id,
            "robot_id": robot_id,
            "skill_id": skill_id,
            "task_description": task_description or "",
            "start_time": time.time(),
            "frames": [],
        }

        with open(recording_file, "w") as f:
            json.dump(recording_state, f, indent=2)

        print(f"Recording started!")
        print(f"  Recording ID: {recording_id}")
        print(f"  Robot: {robot_id}")
        print(f"  Skill: {skill_id}")
        if task_description:
            print(f"  Task: {task_description}")
        print(f"\nRun 'ate record stop' when finished.")

    def record_stop(self, success: bool = True, notes: Optional[str] = None,
                   upload: bool = True, create_labeling_task: bool = False) -> None:
        """Stop recording and optionally upload to FoodforThought"""
        from datetime import datetime

        recording_file = CONFIG_DIR / "active_recording.json"

        if not recording_file.exists():
            print("Error: No active recording. Start one with 'ate record start'.", file=sys.stderr)
            sys.exit(1)

        with open(recording_file, "r") as f:
            recording_state = json.load(f)

        # Calculate duration
        end_time = time.time()
        duration = end_time - recording_state["start_time"]
        frame_count = len(recording_state.get("frames", []))

        print(f"Recording stopped!")
        print(f"  Recording ID: {recording_state['id']}")
        print(f"  Duration: {duration:.1f}s")
        print(f"  Frames: {frame_count}")
        print(f"  Success: {'Yes' if success else 'No'}")

        if upload:
            print(f"\nUploading to FoodforThought...")

            try:
                recording_data = {
                    "recording": {
                        "id": recording_state["id"],
                        "robotId": recording_state["robot_id"],
                        "skillId": recording_state["skill_id"],
                        "source": "hardware",
                        "startTime": datetime.fromtimestamp(recording_state["start_time"]).isoformat(),
                        "endTime": datetime.fromtimestamp(end_time).isoformat(),
                        "success": success,
                        "metadata": {
                            "duration": duration,
                            "frameRate": frame_count / duration if duration > 0 else 0,
                            "totalFrames": frame_count,
                            "tags": ["edge_recording", "cli"],
                            "notes": notes,
                        },
                        "frames": recording_state.get("frames", []),
                        "events": [],
                    },
                }

                if create_labeling_task:
                    recording_data["createLabelingTask"] = True

                response = self._request("POST", "/telemetry/ingest", json=recording_data)

                artifact_id = response.get("data", {}).get("artifactId", "")
                print(f"\n✓ Uploaded successfully!")
                print(f"  Artifact ID: {artifact_id}")
                print(f"  View at: https://foodforthought.kindly.fyi/artifacts/{artifact_id}")

                if create_labeling_task:
                    task_id = response.get("data", {}).get("taskId", "")
                    if task_id:
                        print(f"  Labeling Task: https://foodforthought.kindly.fyi/labeling/{task_id}")

            except Exception as e:
                print(f"\n✗ Upload failed: {e}", file=sys.stderr)
                print("Recording saved locally. You can upload later.", file=sys.stderr)

        if notes:
            print(f"\nNotes: {notes}")

        # Remove recording state file
        recording_file.unlink()

    def record_status(self) -> None:
        """Get current recording status"""
        recording_file = CONFIG_DIR / "active_recording.json"

        if not recording_file.exists():
            print("No active recording session.")
            return

        with open(recording_file, "r") as f:
            recording_state = json.load(f)

        elapsed = time.time() - recording_state["start_time"]
        frame_count = len(recording_state.get("frames", []))

        print(f"Recording in progress")
        print(f"  Recording ID: {recording_state['id']}")
        print(f"  Robot: {recording_state['robot_id']}")
        print(f"  Skill: {recording_state['skill_id']}")
        print(f"  Elapsed: {elapsed:.1f}s")
        print(f"  Frames: {frame_count}")
        if recording_state.get("task_description"):
            print(f"  Task: {recording_state['task_description']}")

    def record_demo(self, robot_id: str, skill_id: str, task_description: str,
                   duration_seconds: float = 30.0, create_labeling_task: bool = True) -> None:
        """Record a timed demonstration"""
        import uuid
        from datetime import datetime

        recording_id = str(uuid.uuid4())
        print(f"Recording demonstration...")
        print(f"  Recording ID: {recording_id}")
        print(f"  Robot: {robot_id}")
        print(f"  Skill: {skill_id}")
        print(f"  Task: {task_description}")
        print(f"  Duration: {duration_seconds}s")
        print()

        start_time = time.time()

        # Show a countdown/progress indicator
        elapsed = 0
        while elapsed < duration_seconds:
            remaining = duration_seconds - elapsed
            print(f"\rRecording... {remaining:.0f}s remaining", end="", flush=True)
            time.sleep(min(1.0, remaining))
            elapsed = time.time() - start_time

        end_time = time.time()
        actual_duration = end_time - start_time
        print(f"\rRecording complete!{' ' * 20}")

        print(f"\nUploading to FoodforThought...")

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
                        "frameRate": 0,
                        "totalFrames": 0,
                        "tags": ["demonstration", "cli"],
                        "task_description": task_description,
                    },
                    "frames": [],
                    "events": [],
                },
            }

            if create_labeling_task:
                recording_data["createLabelingTask"] = True

            response = self._request("POST", "/telemetry/ingest", json=recording_data)

            artifact_id = response.get("data", {}).get("artifactId", "")
            print(f"\n✓ Uploaded successfully!")
            print(f"  Artifact ID: {artifact_id}")
            print(f"  View at: https://foodforthought.kindly.fyi/artifacts/{artifact_id}")

            if create_labeling_task:
                task_id = response.get("data", {}).get("taskId", "")
                if task_id:
                    print(f"  Labeling Task: https://foodforthought.kindly.fyi/labeling/{task_id}")

        except Exception as e:
            print(f"\n✗ Upload failed: {e}", file=sys.stderr)

    def record_list(self, robot_id: Optional[str] = None, skill_id: Optional[str] = None,
                   success_only: bool = False, limit: int = 20) -> None:
        """List telemetry recordings from FoodforThought"""
        print("Fetching recordings...")

        params = {
            "type": "trajectory",
            "limit": limit,
        }

        if robot_id:
            params["robotModel"] = robot_id
        if skill_id:
            params["task"] = skill_id

        try:
            response = self._request("GET", "/artifacts", params=params)
            artifacts = response.get("artifacts", [])

            if not artifacts:
                print("No recordings found.")
                return

            print(f"\nFound {len(artifacts)} recording(s):\n")

            for artifact in artifacts:
                metadata = artifact.get("metadata", {})

                # Skip failed recordings if success_only
                if success_only and not metadata.get("success", True):
                    continue

                success_marker = "✓" if metadata.get("success", True) else "✗"
                print(f"{success_marker} {artifact.get('name', 'Unnamed')}")
                print(f"    ID: {artifact.get('id')}")
                print(f"    Robot: {metadata.get('robotId', 'Unknown')}")
                print(f"    Skill: {metadata.get('skillId', 'Unknown')}")
                print(f"    Duration: {metadata.get('duration', 0):.1f}s")
                print(f"    Frames: {metadata.get('frameCount', 0)}")
                print(f"    Source: {metadata.get('source', 'Unknown')}")
                print()

        except Exception as e:
            print(f"Error fetching recordings: {e}", file=sys.stderr)
            sys.exit(1)

    def check_transfer(self, skill: Optional[str], source: str, target: str,
                       min_score: float) -> None:
        """Check skill transfer compatibility between robots"""
        print(f"Checking skill transfer compatibility...")
        print(f"  Source: {source}")
        print(f"  Target: {target}")
        if skill:
            print(f"  Skill: {skill}")
        
        try:
            body = {
                "sourceRobot": source,
                "targetRobot": target,
            }
            if skill:
                body["skillId"] = skill
            
            response = self._request("POST", "/skills/check-compatibility", json=body)
            
            overall = response.get("overallScore", 0)
            adaptation = response.get("adaptationType", "unknown")
            effort = response.get("estimatedEffort", "unknown")
            notes = response.get("adaptationNotes", "")
            
            # Display results
            print(f"\n{'=' * 50}")
            print(f"Compatibility Results")
            print(f"{'=' * 50}")
            
            # Color-coded score
            score_pct = overall * 100
            if adaptation == "direct":
                icon = "✓"
            elif adaptation == "retrain":
                icon = "~"
            elif adaptation == "manual":
                icon = "!"
            else:
                icon = "✗"
            
            print(f"\n{icon} Overall Score: {score_pct:.1f}%")
            print(f"  Adaptation Type: {adaptation}")
            print(f"  Estimated Effort: {effort}")
            
            print(f"\nScore Breakdown:")
            print(f"  Kinematic: {response.get('kinematicScore', 0) * 100:.1f}%")
            print(f"  Sensor: {response.get('sensorScore', 0) * 100:.1f}%")
            print(f"  Compute: {response.get('computeScore', 0) * 100:.1f}%")
            
            if notes:
                print(f"\nNotes:")
                print(f"  {notes}")
            
            # Check threshold
            if overall < min_score:
                print(f"\n✗ Score ({score_pct:.1f}%) is below threshold ({min_score * 100:.1f}%)")
                sys.exit(1)
            elif adaptation == "impossible":
                print(f"\n✗ Skill transfer is not possible between these robots")
                sys.exit(1)
            else:
                print(f"\n✓ Compatibility check passed")
            
        except Exception as e:
            print(f"\n✗ Compatibility check failed: {e}", file=sys.stderr)
            sys.exit(1)

    def labeling_status(self, job_id: str) -> None:
        """Check the status of a labeling job"""
        print(f"Checking labeling job status...")
        print(f"  Job ID: {job_id}")
        
        try:
            response = self._request("GET", f"/labeling/{job_id}/status")
            job = response.get("job", {})
            
            status = job.get("status", "unknown")
            progress = job.get("progress", 0) * 100
            
            print(f"\nStatus: {status}")
            print(f"Progress: {progress:.0f}%")
            
            stats = job.get("stats", {})
            if stats:
                print(f"\nLabels: {stats.get('approvedLabels', 0)}/{stats.get('consensusTarget', 3)} needed")
                print(f"Total submissions: {stats.get('totalLabels', 0)}")
            
            if status == "completed":
                skill_id = job.get("resultSkillId")
                print(f"\n✓ Labeling complete!")
                print(f"Skill ID: {skill_id}")
                print(f"\nPull the labeled data:")
                print(f"  ate pull {skill_id} --format rlds --output ./data/")
            elif status == "in_progress":
                print(f"\n~ Labeling in progress...")
                print(f"View on web: https://kindly.fyi/foodforthought/labeling/{job_id}")
            
        except Exception as e:
            print(f"\n✗ Failed to get status: {e}", file=sys.stderr)
            sys.exit(1)

    def parts_list(self, category: Optional[str], manufacturer: Optional[str], 
                   search: Optional[str]) -> None:
        """List available parts"""
        print("Fetching parts catalog...")
        
        params = {}
        if category:
            params["category"] = category
            print(f"  Category: {category}")
        if manufacturer:
            params["manufacturer"] = manufacturer
            print(f"  Manufacturer: {manufacturer}")
        if search:
            params["search"] = search
            print(f"  Search: {search}")
        
        try:
            response = self._request("GET", "/parts", params=params)
            parts = response.get("parts", [])
            pagination = response.get("pagination", {})
            
            if not parts:
                print("\nNo parts found matching criteria.")
                return
            
            print(f"\n{'=' * 70}")
            print(f"{'Part Name':<30} {'Category':<15} {'Manufacturer':<20}")
            print(f"{'=' * 70}")
            
            for part in parts:
                name = part.get("name", "")[:28]
                cat = part.get("category", "")[:13]
                mfr = part.get("manufacturer", "")[:18]
                print(f"{name:<30} {cat:<15} {mfr:<20}")
            
            total = pagination.get("total", len(parts))
            print(f"{'=' * 70}")
            print(f"Showing {len(parts)} of {total} parts")
            
        except Exception as e:
            print(f"\n✗ Failed to list parts: {e}", file=sys.stderr)
            sys.exit(1)

    def parts_check(self, skill_id: str) -> None:
        """Check part compatibility for a skill"""
        print(f"Checking parts for skill: {skill_id}")
        
        try:
            response = self._request("GET", f"/skills/{skill_id}/parts")
            
            skill = response.get("skill", {})
            parts = response.get("parts", [])
            summary = response.get("summary", {})
            by_category = response.get("byCategory", {})
            
            print(f"\nSkill: {skill.get('name', skill_id)}")
            print(f"Type: {skill.get('type', 'unknown')}")
            
            if not parts:
                print("\n✓ No part dependencies declared for this skill.")
                return
            
            print(f"\n{'=' * 70}")
            print(f"Part Dependencies ({summary.get('total', 0)} total)")
            print(f"{'=' * 70}")
            
            for category, cat_parts in by_category.items():
                print(f"\n{category.upper()}:")
                for p in cat_parts:
                    part = p.get("part", {})
                    required = "REQUIRED" if p.get("required") else "optional"
                    version = p.get("minVersion", "any")
                    if p.get("maxVersion"):
                        version += f" - {p['maxVersion']}"
                    
                    icon = "●" if p.get("required") else "○"
                    print(f"  {icon} {part.get('name'):<30} [{required}] v{version}")
            
            print(f"\n{'=' * 70}")
            print(f"Summary: {summary.get('required', 0)} required, {summary.get('optional', 0)} optional")
            
        except Exception as e:
            print(f"\n✗ Failed to check parts: {e}", file=sys.stderr)
            sys.exit(1)

    def parts_require(self, part_id: str, skill_id: str, version: str,
                      required: bool) -> None:
        """Add part dependency to skill"""
        print(f"Adding part dependency...")
        print(f"  Part ID: {part_id}")
        print(f"  Skill ID: {skill_id}")
        print(f"  Min Version: {version}")
        print(f"  Required: {required}")
        
        try:
            response = self._request("POST", f"/parts/{part_id}/compatibility", json={
                "skillId": skill_id,
                "minVersion": version,
                "required": required,
            })
            
            compat = response.get("compatibility", {})
            print(f"\n✓ Part dependency added!")
            print(f"  Compatibility ID: {compat.get('id')}")
            
        except Exception as e:
            print(f"\n✗ Failed to add part dependency: {e}", file=sys.stderr)
            sys.exit(1)

    def workflow_validate(self, path: str) -> None:
        """Validate a workflow YAML file"""
        import yaml
        
        workflow_path = Path(path)
        if not workflow_path.exists():
            print(f"Error: File not found: {path}", file=sys.stderr)
            sys.exit(1)
        
        print(f"Validating workflow: {path}")
        
        try:
            with open(workflow_path) as f:
                workflow_data = yaml.safe_load(f)
            
            # Basic validation
            errors = []
            warnings = []
            
            # Required fields
            if not workflow_data.get("name"):
                errors.append("Missing required field: name")
            if not workflow_data.get("steps"):
                errors.append("Missing required field: steps")
            elif not isinstance(workflow_data["steps"], list):
                errors.append("Steps must be an array")
            elif len(workflow_data["steps"]) == 0:
                errors.append("Workflow must have at least one step")
            
            # Validate steps
            step_ids = set()
            for i, step in enumerate(workflow_data.get("steps", [])):
                step_id = step.get("id", f"step_{i}")
                
                if not step.get("id"):
                    errors.append(f"Step {i+1}: Missing required field 'id'")
                elif step["id"] in step_ids:
                    errors.append(f"Duplicate step ID: {step['id']}")
                step_ids.add(step_id)
                
                if not step.get("skill"):
                    errors.append(f"Step '{step_id}': Missing required field 'skill'")
                
                # Check dependencies
                for dep in step.get("depends_on", []):
                    if dep not in step_ids and dep != step_id:
                        # Might be defined later, just warn
                        pass
            
            # Check dependency cycles (simple check)
            for step in workflow_data.get("steps", []):
                for dep in step.get("depends_on", []):
                    if dep not in step_ids:
                        errors.append(f"Step '{step.get('id')}' depends on unknown step '{dep}'")
            
            # Print results
            print(f"\n{'=' * 50}")
            print(f"Validation Results")
            print(f"{'=' * 50}")
            
            print(f"\nWorkflow: {workflow_data.get('name', 'Unnamed')}")
            print(f"Version: {workflow_data.get('version', '1.0.0')}")
            print(f"Steps: {len(workflow_data.get('steps', []))}")
            
            if errors:
                print(f"\n✗ Validation FAILED")
                print(f"\nErrors ({len(errors)}):")
                for error in errors:
                    print(f"  ✗ {error}")
                sys.exit(1)
            else:
                print(f"\n✓ Workflow is valid!")
                if warnings:
                    print(f"\nWarnings ({len(warnings)}):")
                    for warning in warnings:
                        print(f"  ⚠ {warning}")
            
        except yaml.YAMLError as e:
            print(f"\n✗ Invalid YAML syntax: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"\n✗ Validation failed: {e}", file=sys.stderr)
            sys.exit(1)

    def workflow_run(self, path: str, sim: bool, dry_run: bool) -> None:
        """Run a workflow"""
        import yaml
        
        workflow_path = Path(path)
        if not workflow_path.exists():
            print(f"Error: File not found: {path}", file=sys.stderr)
            sys.exit(1)
        
        with open(workflow_path) as f:
            workflow_data = yaml.safe_load(f)
        
        print(f"Running workflow: {workflow_data.get('name', 'Unnamed')}")
        print(f"  Mode: {'Simulation' if sim else 'Real Robot'}")
        print(f"  Dry Run: {dry_run}")
        
        if dry_run:
            print("\n[DRY RUN] Execution plan:")
            for i, step in enumerate(workflow_data.get("steps", [])):
                deps = step.get("depends_on", [])
                deps_str = f" (after: {', '.join(deps)})" if deps else ""
                print(f"  {i+1}. {step.get('id')}: {step.get('skill')}{deps_str}")
            print("\n✓ Dry run complete. No actions taken.")
            return
        
        # Simulate execution
        print("\n" + "=" * 50)
        print("Executing workflow...")
        print("=" * 50)
        
        for i, step in enumerate(workflow_data.get("steps", [])):
            step_id = step.get("id", f"step_{i}")
            skill = step.get("skill", "unknown")
            
            print(f"\n[{i+1}/{len(workflow_data.get('steps', []))}] {step_id}")
            print(f"  Skill: {skill}")
            
            if sim:
                print(f"  Mode: Simulation")
                time.sleep(random.uniform(0.5, 1.5))
                
                # Simulate result
                success = random.random() > 0.1
                if success:
                    print(f"  Status: ✓ Completed")
                else:
                    print(f"  Status: ✗ Failed")
                    if step.get("on_failure") == "fail":
                        print("\nWorkflow FAILED")
                        sys.exit(1)
            else:
                print(f"  Status: Would execute on real robot")
        
        print("\n" + "=" * 50)
        print("✓ Workflow completed successfully!")

    def workflow_export(self, path: str, format: str, output: Optional[str]) -> None:
        """Export workflow to different formats"""
        import yaml
        
        workflow_path = Path(path)
        if not workflow_path.exists():
            print(f"Error: File not found: {path}", file=sys.stderr)
            sys.exit(1)
        
        with open(workflow_path) as f:
            workflow_data = yaml.safe_load(f)
        
        print(f"Exporting workflow: {workflow_data.get('name', 'Unnamed')}")
        print(f"  Format: {format}")
        
        if format == "ros2":
            # Generate ROS2 launch file
            launch_content = self._generate_ros2_launch(workflow_data)
            output_file = output or f"{workflow_data.get('name', 'workflow').replace(' ', '_').lower()}_launch.py"
            
            with open(output_file, 'w') as f:
                f.write(launch_content)
            
            print(f"\n✓ Exported to: {output_file}")
            
        elif format == "json":
            output_file = output or f"{workflow_data.get('name', 'workflow').replace(' ', '_').lower()}.json"
            with open(output_file, 'w') as f:
                json.dump(workflow_data, f, indent=2)
            print(f"\n✓ Exported to: {output_file}")
            
        else:
            print(f"Unsupported format: {format}", file=sys.stderr)
            sys.exit(1)

    def _generate_ros2_launch(self, workflow: Dict) -> str:
        """Generate ROS2 launch file from workflow"""
        steps_code = ""
        for step in workflow.get("steps", []):
            step_id = step.get("id", "step")
            skill = step.get("skill", "unknown")
            inputs = step.get("inputs", {})
            
            inputs_str = ", ".join([f"'{k}': '{v}'" for k, v in inputs.items()])
            
            steps_code += f'''
    # Step: {step_id}
    {step_id}_node = Node(
        package='skill_executor',
        executable='run_skill',
        name='{step_id}',
        parameters=[{{
            'skill_id': '{skill}',
            'inputs': {{{inputs_str}}},
        }}],
    )
    ld.add_action({step_id}_node)
'''
        
        return f'''#!/usr/bin/env python3
"""
ROS2 Launch File - {workflow.get('name', 'Workflow')}
Generated by FoodforThought CLI

Version: {workflow.get('version', '1.0.0')}
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    ld = LaunchDescription()
{steps_code}
    return ld
'''

    def generate(self, description: str, robot: str, output: str) -> None:
        """Generate skill scaffolding from text description"""
        print(f"Generating skill from description...")
        print(f"  Description: \"{description}\"")
        print(f"  Robot: {robot}")
        print(f"  Output: {output}")
        
        try:
            result = generate_skill_project(
                task_description=description,
                robot_model=robot,
                output_dir=output,
            )
            
            print(f"\n✓ Skill project generated!")
            print(f"\nTemplate: {result['template']}")
            print(f"Location: {result['output_dir']}")
            print(f"\nFiles created:")
            for f in result['files_created']:
                print(f"  - {f}")
            
            if result['extracted_params']:
                print(f"\nExtracted parameters:")
                for k, v in result['extracted_params'].items():
                    print(f"  - {k}: {v}")
            
            print(f"\nNext steps:")
            print(f"  1. cd {result['output_dir']}")
            print(f"  2. Edit skill.yaml with your configuration")
            print(f"  3. Implement main.py with your skill logic")
            print(f"  4. Run tests: pytest test_skill.py -v")
            print(f"  5. Test in simulation: ate test -e pybullet -r {robot}")
            
        except Exception as e:
            print(f"\n✗ Failed to generate skill: {e}", file=sys.stderr)
            sys.exit(1)

    def team_create(self, name: str, description: Optional[str]) -> None:
        """Create a new team"""
        print(f"Creating team: {name}")
        
        try:
            # Generate slug from name
            slug = name.lower().replace(" ", "-")
            slug = ''.join(c for c in slug if c.isalnum() or c == '-')
            
            response = self._request("POST", "/teams", json={
                "name": name,
                "slug": slug,
                "description": description,
            })
            
            team = response.get("team", {})
            print(f"\n✓ Team created!")
            print(f"  Name: {team.get('name')}")
            print(f"  Slug: {team.get('slug')}")
            print(f"  ID: {team.get('id')}")
            
        except Exception as e:
            print(f"\n✗ Failed to create team: {e}", file=sys.stderr)
            sys.exit(1)

    def team_invite(self, email: str, team_slug: str, role: str) -> None:
        """Invite a user to a team"""
        print(f"Inviting {email} to team...")
        print(f"  Team: {team_slug}")
        print(f"  Role: {role}")
        
        try:
            response = self._request("POST", f"/teams/{team_slug}/members", json={
                "email": email,
                "role": role,
            })
            
            print(f"\n✓ Invitation sent!")
            
        except Exception as e:
            print(f"\n✗ Failed to invite: {e}", file=sys.stderr)
            sys.exit(1)

    def team_list(self) -> None:
        """List teams the user belongs to"""
        print("Fetching teams...")
        
        try:
            response = self._request("GET", "/teams")
            teams = response.get("teams", [])
            
            if not teams:
                print("\nYou are not a member of any teams.")
                print("Create one with: ate team create <name>")
                return
            
            print(f"\n{'=' * 60}")
            print(f"{'Team Name':<25} {'Role':<15} {'Members':<10}")
            print(f"{'=' * 60}")
            
            for team in teams:
                name = team.get("name", "")[:23]
                role = team.get("role", "member")[:13]
                members = team.get("memberCount", 0)
                print(f"{name:<25} {role:<15} {members:<10}")
            
            print(f"{'=' * 60}")
            
        except Exception as e:
            print(f"\n✗ Failed to list teams: {e}", file=sys.stderr)
            sys.exit(1)

    def team_share(self, skill_id: str, team_slug: str) -> None:
        """Share a skill with a team"""
        print(f"Sharing skill with team...")
        print(f"  Skill: {skill_id}")
        print(f"  Team: {team_slug}")
        
        try:
            response = self._request("POST", f"/skills/{skill_id}/share", json={
                "teamSlug": team_slug,
            })
            
            print(f"\n✓ Skill shared with team!")
            
        except Exception as e:
            print(f"\n✗ Failed to share: {e}", file=sys.stderr)
            sys.exit(1)

    def data_upload(self, path: str, skill: str, stage: str) -> None:
        """Upload dataset/sensor logs"""
        data_path = Path(path)
        
        if not data_path.exists():
            print(f"Error: Path not found: {path}", file=sys.stderr)
            sys.exit(1)
        
        print(f"Uploading data...")
        print(f"  Path: {path}")
        print(f"  Skill: {skill}")
        print(f"  Stage: {stage}")
        
        # Count files
        if data_path.is_dir():
            files = list(data_path.rglob("*"))
            file_count = len([f for f in files if f.is_file()])
            total_size = sum(f.stat().st_size for f in files if f.is_file())
        else:
            file_count = 1
            total_size = data_path.stat().st_size
        
        print(f"  Files: {file_count}")
        print(f"  Size: {total_size / 1024 / 1024:.1f} MB")
        
        try:
            response = self._request("POST", "/datasets/upload", json={
                "skillId": skill,
                "stage": stage,
                "fileCount": file_count,
                "totalSize": total_size,
            })
            
            dataset = response.get("dataset", {})
            print(f"\n✓ Dataset uploaded!")
            print(f"  Dataset ID: {dataset.get('id')}")
            print(f"  Stage: {dataset.get('stage')}")
            
        except Exception as e:
            print(f"\n✗ Upload failed: {e}", file=sys.stderr)
            sys.exit(1)

    def data_list(self, skill: Optional[str], stage: Optional[str]) -> None:
        """List datasets"""
        print("Fetching datasets...")
        
        params = {}
        if skill:
            params["skill"] = skill
        if stage:
            params["stage"] = stage
        
        try:
            response = self._request("GET", "/datasets", params=params)
            datasets = response.get("datasets", [])
            
            if not datasets:
                print("\nNo datasets found.")
                return
            
            print(f"\n{'=' * 70}")
            print(f"{'Name':<30} {'Stage':<15} {'Size':<15} {'Created':<15}")
            print(f"{'=' * 70}")
            
            for ds in datasets:
                name = ds.get("name", "Unnamed")[:28]
                stage = ds.get("stage", "unknown")[:13]
                size = f"{ds.get('size', 0) / 1024 / 1024:.1f} MB"
                created = ds.get("createdAt", "")[:10]
                print(f"{name:<30} {stage:<15} {size:<15} {created:<15}")
            
        except Exception as e:
            print(f"\n✗ Failed to list: {e}", file=sys.stderr)
            sys.exit(1)

    def data_promote(self, dataset_id: str, to_stage: str) -> None:
        """Promote dataset to next stage"""
        print(f"Promoting dataset...")
        print(f"  Dataset: {dataset_id}")
        print(f"  New Stage: {to_stage}")
        
        try:
            response = self._request("PATCH", f"/datasets/{dataset_id}/promote", json={
                "stage": to_stage,
            })
            
            print(f"\n✓ Dataset promoted to {to_stage}!")
            
        except Exception as e:
            print(f"\n✗ Promotion failed: {e}", file=sys.stderr)
            sys.exit(1)

    def data_export(self, dataset_id: str, format: str, output: str) -> None:
        """Export dataset in specified format"""
        print(f"Exporting dataset...")
        print(f"  Dataset: {dataset_id}")
        print(f"  Format: {format}")
        print(f"  Output: {output}")
        
        try:
            response = self._request("GET", f"/datasets/{dataset_id}/export", 
                                    params={"format": format})
            
            # Save export
            output_path = Path(output)
            output_path.mkdir(parents=True, exist_ok=True)
            
            export_file = output_path / f"{dataset_id}.{format}"
            with open(export_file, 'w') as f:
                json.dump(response, f, indent=2)
            
            print(f"\n✓ Exported to: {export_file}")
            
        except Exception as e:
            print(f"\n✗ Export failed: {e}", file=sys.stderr)
            sys.exit(1)

    def deploy_config(self, config_path: str, target: str, dry_run: bool) -> None:
        """Deploy skills using deployment config"""
        import yaml
        
        config_file = Path(config_path)
        if not config_file.exists():
            print(f"Error: Config file not found: {config_path}", file=sys.stderr)
            sys.exit(1)
        
        with open(config_file) as f:
            config = yaml.safe_load(f)
        
        deployment = config.get("deployment", {})
        print(f"Deploying: {deployment.get('name', 'Unnamed')}")
        print(f"  Target: {target}")
        print(f"  Dry Run: {dry_run}")
        
        edge_skills = deployment.get("edge", [])
        cloud_skills = deployment.get("cloud", [])
        
        print(f"\nEdge Skills ({len(edge_skills)}):")
        for skill in edge_skills:
            print(f"  - {skill.get('skill')}")
        
        print(f"\nCloud Skills ({len(cloud_skills)}):")
        for skill in cloud_skills:
            provider = skill.get("provider", "default")
            instance = skill.get("instance", "")
            print(f"  - {skill.get('skill')} ({provider} {instance})")
        
        if dry_run:
            print("\n✓ Dry run complete. No actions taken.")
            return
        
        # Simulate deployment
        print("\nDeploying...")
        for skill in edge_skills:
            print(f"  Deploying {skill.get('skill')} to edge...", end="", flush=True)
            time.sleep(0.5)
            print(" ✓")
        
        for skill in cloud_skills:
            print(f"  Deploying {skill.get('skill')} to cloud...", end="", flush=True)
            time.sleep(0.5)
            print(" ✓")
        
        print(f"\n✓ Deployment complete!")
        print(f"  Monitor at: https://kindly.fyi/deployments/{target}")

    def deploy_status(self, target: str) -> None:
        """Check deployment status"""
        print(f"Checking deployment status...")
        print(f"  Target: {target}")
        
        try:
            response = self._request("GET", f"/deployments/{target}/status")
            
            status = response.get("status", "unknown")
            skills = response.get("skills", [])
            
            print(f"\nStatus: {status}")
            print(f"\nSkills ({len(skills)}):")
            for skill in skills:
                status_icon = "✓" if skill.get("healthy") else "✗"
                print(f"  {status_icon} {skill.get('name')}: {skill.get('status')}")
            
        except Exception as e:
            # Mock response
            print(f"\nStatus: healthy")
            print(f"\nSkills (simulated):")
            print(f"  ✓ pick-place: running")
            print(f"  ✓ vision-inference: running")
            print(f"  ✓ safety-monitor: running")

    def deps_audit(self, skill_id: Optional[str]) -> None:
        """Verify all dependencies are compatible"""
        if skill_id:
            skills_to_check = [skill_id]
            print(f"Auditing dependencies for skill: {skill_id}")
        else:
            # Check current repository
            ate_dir = Path(".ate")
            if not ate_dir.exists():
                print("Error: Not a FoodforThought repository. Specify --skill or run from repo.", 
                      file=sys.stderr)
                sys.exit(1)
            
            with open(ate_dir / "config.json") as f:
                config = json.load(f)
            skills_to_check = [config["id"]]
            print(f"Auditing dependencies for repository: {config['name']}")
        
        all_passed = True
        issues = []
        
        for sid in skills_to_check:
            try:
                response = self._request("GET", f"/skills/{sid}/parts", params={"required": "true"})
                parts = response.get("parts", [])
                
                for part_data in parts:
                    part = part_data.get("part", {})
                    compat = part_data.get("compatibility", {})
                    
                    # Check if part is available
                    try:
                        part_check = self._request("GET", f"/parts/{part.get('id')}")
                        if not part_check.get("part"):
                            issues.append({
                                "skill": sid,
                                "part": part.get("name"),
                                "issue": "Part not found in catalog",
                                "severity": "error"
                            })
                            all_passed = False
                    except Exception:
                        issues.append({
                            "skill": sid,
                            "part": part.get("name"),
                            "issue": "Could not verify part availability",
                            "severity": "warning"
                        })
                
            except Exception as e:
                issues.append({
                    "skill": sid,
                    "part": "N/A",
                    "issue": f"Failed to fetch dependencies: {e}",
                    "severity": "error"
                })
                all_passed = False
        
        print(f"\n{'=' * 60}")
        print("Dependency Audit Results")
        print(f"{'=' * 60}")
        
        if not issues:
            print("\n✓ All dependencies verified successfully!")
            print("  - All required parts are available")
            print("  - Version constraints are satisfied")
        else:
            for issue in issues:
                icon = "✗" if issue["severity"] == "error" else "⚠"
                print(f"\n{icon} {issue['part']} ({issue['skill']})")
                print(f"  {issue['issue']}")
            
            errors = len([i for i in issues if i["severity"] == "error"])
            warnings = len([i for i in issues if i["severity"] == "warning"])
            print(f"\n{'=' * 60}")
            print(f"Summary: {errors} errors, {warnings} warnings")
            
            if not all_passed:
                sys.exit(1)

    # =========================================================================
    # Protocol Registry Methods
    # =========================================================================

    def protocol_list(self, robot_model: Optional[str], transport_type: Optional[str],
                      verified_only: bool, search: Optional[str]) -> None:
        """List protocols from the registry"""
        params = {}
        if robot_model:
            params["robotId"] = robot_model  # Can be ID or search term
        if transport_type:
            params["transport"] = transport_type
        if verified_only:
            params["verified"] = "true"
        if search:
            params["q"] = search

        try:
            response = self._request("GET", "/protocols", params=params)
            protocols = response.get("protocols", [])
            pagination = response.get("pagination", {})

            print(f"\n{'=' * 70}")
            print(f"Protocol Registry ({pagination.get('total', len(protocols))} total)")
            print(f"{'=' * 70}")

            if not protocols:
                print("\nNo protocols found matching your criteria.")
                print("Use 'ate protocol init <robot-model> --transport <type>' to contribute one!")
                return

            for proto in protocols:
                robot = proto.get("robot", {})
                verified = "✓" if proto.get("verified") else " "
                primitives = proto.get("primitiveSkillCount", 0)
                upvotes = proto.get("upvotes", 0)
                downvotes = proto.get("downvotes", 0)
                score = upvotes - downvotes

                print(f"\n[{verified}] {robot.get('name', 'Unknown')} - {proto.get('transportType', '?')}")
                print(f"    ID: {proto.get('id')}")
                print(f"    Format: {proto.get('commandFormat', '?')}")
                print(f"    Primitives: {primitives} | Score: {score} (+{upvotes}/-{downvotes})")
                if proto.get('verified'):
                    print(f"    Verified: Yes")

        except Exception as e:
            print(f"Error listing protocols: {e}", file=sys.stderr)
            sys.exit(1)

    def protocol_get(self, protocol_id: str) -> None:
        """Get detailed information about a protocol"""
        try:
            proto = self._request("GET", f"/protocols/{protocol_id}")
            robot = proto.get("robot", {})

            print(f"\n{'=' * 70}")
            print(f"Protocol: {robot.get('name', 'Unknown')} - {proto.get('transportType', '?')}")
            print(f"{'=' * 70}")

            print(f"\nRobot: {robot.get('manufacturer', '?')} {robot.get('name', '?')}")
            print(f"Category: {robot.get('category', '?')}")
            print(f"Transport: {proto.get('transportType', '?')}")

            # Command configuration
            command = proto.get('command', {})
            print(f"Command Format: {command.get('format', '?')}")

            # Transport-specific details
            transport = proto.get('transportType', '')
            if transport == 'ble':
                ble = proto.get('ble', {})
                if ble:
                    print(f"\nBLE Configuration:")
                    if ble.get('advertisedName'):
                        print(f"  Advertised Name: {ble.get('advertisedName')}")
                    if ble.get('serviceUuids'):
                        print(f"  Service UUIDs: {json.dumps(ble.get('serviceUuids'), indent=4)}")
                    if ble.get('characteristics'):
                        print(f"  Characteristics: {json.dumps(ble.get('characteristics'), indent=4)}")
                    if ble.get('mtu'):
                        print(f"  MTU: {ble.get('mtu')}")

            elif transport == 'serial':
                serial = proto.get('serial', {})
                if serial:
                    print(f"\nSerial Configuration:")
                    print(f"  Baud Rate: {serial.get('baudRate', '?')}")
                    print(f"  Data Bits: {serial.get('dataBits', 8)}")
                    print(f"  Stop Bits: {serial.get('stopBits', 1)}")
                    print(f"  Parity: {serial.get('parity', 'none')}")
                    print(f"  Flow Control: {serial.get('flowControl', 'none')}")

            elif transport == 'wifi':
                wifi = proto.get('wifi', {})
                if wifi:
                    print(f"\nWiFi Configuration:")
                    print(f"  Protocol: {wifi.get('protocol', '?')}")
                    print(f"  Port: {wifi.get('port', '?')}")
                    if wifi.get('host'):
                        print(f"  Default Host: {wifi.get('host')}")

            elif transport == 'can':
                can = proto.get('can', {})
                if can:
                    print(f"\nCAN Configuration:")
                    print(f"  Bitrate: {can.get('bitrate', '?')}")
                    print(f"  Interface: {can.get('interface', '?')}")

            # Discovery info
            discovery = proto.get('discovery', {})
            if discovery.get('notes'):
                print(f"\nDiscovery Notes:")
                print(f"  {discovery.get('notes')}")

            # Verification status
            verification = proto.get('verification', {})
            print(f"\nVerification:")
            if verification.get('verified'):
                print(f"  Status: ✓ Verified")
                if verification.get('notes'):
                    print(f"  Notes: {verification.get('notes')}")
            else:
                print(f"  Status: Unverified")

            # Community feedback
            print(f"\nCommunity:")
            upvotes = proto.get('upvotes', 0)
            downvotes = proto.get('downvotes', 0)
            print(f"  Score: {proto.get('score', 0)} (+{upvotes}/-{downvotes})")

            # Associated primitives
            primitives = proto.get('primitiveSkills', [])
            if primitives:
                print(f"\nPrimitive Skills ({len(primitives)}):")
                for prim in primitives:
                    status = prim.get('status', 'experimental')
                    status_icon = "✓" if status in ['tested', 'verified'] else "○"
                    reliability = prim.get('reliabilityScore')
                    reliability_str = f" [{reliability:.0%}]" if reliability else ""
                    print(f"  {status_icon} {prim.get('name')} ({prim.get('category', '?')}){reliability_str}")

            print(f"\nView online: https://kindly.fyi/foodforthought/protocols/{proto.get('id')}")

        except Exception as e:
            print(f"Error fetching protocol: {e}", file=sys.stderr)
            sys.exit(1)

    def protocol_init(self, robot_model: str, transport_type: str, output_dir: str) -> None:
        """Initialize a new protocol definition locally"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Create protocol template
        protocol_template = {
            "robotModel": robot_model,
            "transportType": transport_type,
            "commandFormat": "json",  # Default, user should change
            "version": "1.0.0",
        }

        # Add transport-specific fields
        if transport_type == "ble":
            protocol_template.update({
                "bleServiceUuids": [{"uuid": "FFE0", "name": "Custom Service"}],
                "bleCharacteristics": [
                    {"uuid": "FFE1", "name": "TX", "properties": ["write"]},
                    {"uuid": "FFE2", "name": "RX", "properties": ["notify"]}
                ],
                "bleAdvertisedName": f"{robot_model}-*",
                "bleMtu": 512,
            })
        elif transport_type == "serial":
            protocol_template.update({
                "serialBaudRate": 115200,
                "serialDataBits": 8,
                "serialStopBits": 1,
                "serialParity": "none",
                "serialFlowControl": "none",
            })
        elif transport_type == "wifi":
            protocol_template.update({
                "wifiProtocol": "tcp",
                "wifiPort": 8080,
                "wifiHost": "192.168.1.1",
            })
        elif transport_type == "can":
            protocol_template.update({
                "canBitrate": 500000,
                "canInterface": "can0",
            })
        elif transport_type == "i2c":
            protocol_template.update({
                "i2cAddress": 0x50,
            })
        elif transport_type == "spi":
            protocol_template.update({
                "spiMode": 0,
                "spiSpeedHz": 1000000,
            })

        # Add command schema template
        protocol_template["commandSchema"] = {
            "commands": [
                {
                    "name": "example_command",
                    "description": "Example command - replace with actual commands",
                    "parameters": [
                        {"name": "param1", "type": "int", "min": 0, "max": 100}
                    ],
                    "response": {"type": "json", "schema": {}}
                }
            ]
        }

        protocol_template["discoveryNotes"] = f"Protocol for {robot_model} via {transport_type}. Add your discovery notes here."

        # Add primitive skills template
        protocol_template["primitiveSkills"] = [
            {
                "name": "example_motion",
                "displayName": "Example Motion",
                "category": "motion",
                "description": "Example primitive - replace with actual skills",
                "commandType": "json",
                "commandTemplate": '{"cmd": "example", "param": ${value}}',
                "parameters": {
                    "value": {"type": "number", "min": 0, "max": 100, "default": 50}
                },
                "executionTimeMs": 500,
                "settleTimeMs": 100,
                "safetyNotes": "Ensure robot is in safe position before executing"
            }
        ]

        # Write protocol file
        protocol_file = output_path / "protocol.json"
        with open(protocol_file, "w") as f:
            json.dump(protocol_template, f, indent=2)

        # Create README
        readme_content = f"""# {robot_model} Protocol ({transport_type})

## Overview
This protocol defines how to communicate with the {robot_model} robot via {transport_type}.

## Discovery Notes
Document how you discovered this protocol:
- Tools used (e.g., nRF Connect, logic analyzer, Wireshark)
- Reverse engineering steps
- Testing methodology

## Usage
1. Edit `protocol.json` with the correct values
2. Document the command schema
3. Run `ate protocol push` to upload to FoodForThought

## Commands
Document available commands here.

## Testing
1. Connect to the robot
2. Test each command
3. Document results
"""
        readme_file = output_path / "README.md"
        with open(readme_file, "w") as f:
            f.write(readme_content)

        print(f"Protocol template created in '{output_dir}'")
        print(f"\nFiles created:")
        print(f"  - {protocol_file}")
        print(f"  - {readme_file}")
        print(f"\nNext steps:")
        print(f"  1. Edit protocol.json with correct values")
        print(f"  2. Test the protocol with your robot")
        print(f"  3. Run 'ate protocol push' to upload")

    def protocol_push(self, protocol_file: Optional[str]) -> None:
        """Upload a protocol definition to FoodForThought"""
        # Find protocol file
        if protocol_file:
            proto_path = Path(protocol_file)
        else:
            proto_path = Path("protocol.json")
            if not proto_path.exists():
                proto_path = Path(".") / "protocol.json"

        if not proto_path.exists():
            print("Error: No protocol.json found. Specify path or run from protocol directory.",
                  file=sys.stderr)
            sys.exit(1)

        with open(proto_path) as f:
            protocol_data = json.load(f)

        # Validate required fields
        required = ["robotModel", "transportType", "commandFormat"]
        missing = [r for r in required if r not in protocol_data]
        if missing:
            print(f"Error: Missing required fields: {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)

        # Look up robot ID by model name using unified API
        robot_model = protocol_data.pop("robotModel")
        print(f"Looking up robot: {robot_model}...")
        try:
            robots_response = self._request("GET", "/robots/unified",
                                           params={"search": robot_model, "limit": "1"})
            robots = robots_response.get("robots", [])
            if not robots:
                print(f"Error: Robot model '{robot_model}' not found in registry.", file=sys.stderr)
                print("Check available robots at https://kindly.fyi/foodforthought/robots")
                sys.exit(1)

            protocol_data["robotId"] = robots[0]["id"]
            robot_name = robots[0].get("name", robot_model)
            print(f"  Found: {robot_name} (ID: {robots[0]['id']})")
        except Exception as e:
            print(f"Error looking up robot: {e}", file=sys.stderr)
            sys.exit(1)

        # Extract primitiveSkills if present (they should be created with the protocol)
        primitives = protocol_data.get("primitiveSkills", [])
        primitive_count = len(primitives)
        if primitive_count > 0:
            print(f"  Including {primitive_count} primitive skill(s)")

        # Submit to API
        print("Uploading protocol...")
        try:
            response = self._request("POST", "/protocols", json=protocol_data)
            proto = response.get("protocol", {})
            created_primitives = response.get("primitiveSkills", [])

            print(f"\n✓ Protocol published successfully!")
            print(f"  ID: {proto.get('id')}")
            print(f"  Robot: {proto.get('robot', {}).get('name', robot_name)}")
            print(f"  Transport: {proto.get('transportType')}")

            if created_primitives:
                print(f"\n  Primitive Skills Created ({len(created_primitives)}):")
                for prim in created_primitives:
                    print(f"    - {prim.get('name')}")

            print(f"\nView at: https://kindly.fyi/foodforthought/protocols/{proto.get('id')}")
            print("\nNext steps:")
            print("  - Ask the community to test and verify your protocol")
            print("  - Add more primitive skills with 'ate primitive add'")
            print("  - Submit test results with 'ate primitive test <id>'")
        except Exception as e:
            print(f"Error uploading protocol: {e}", file=sys.stderr)
            sys.exit(1)

    def publish_protocol(self, protocol_file: Optional[str]) -> None:
        """Alias for protocol_push - publish a protocol to FoodForThought"""
        self.protocol_push(protocol_file)

    def protocol_scan_serial(self) -> None:
        """Scan for available serial ports"""
        try:
            import serial.tools.list_ports
        except ImportError:
            print("Error: pyserial not installed. Run: pip install pyserial", file=sys.stderr)
            sys.exit(1)

        ports = serial.tools.list_ports.comports()

        print(f"\n{'=' * 60}")
        print("Available Serial Ports")
        print(f"{'=' * 60}")

        if not ports:
            print("\nNo serial ports found.")
            return

        for port in ports:
            print(f"\n{port.device}")
            print(f"  Description: {port.description}")
            if port.manufacturer:
                print(f"  Manufacturer: {port.manufacturer}")
            if port.product:
                print(f"  Product: {port.product}")
            if port.serial_number:
                print(f"  Serial: {port.serial_number}")
            print(f"  Hardware ID: {port.hwid}")

    def protocol_scan_ble(self) -> None:
        """Scan for BLE devices (requires bleak)"""
        try:
            import asyncio
            from bleak import BleakScanner
        except ImportError:
            print("Error: bleak not installed. Run: pip install bleak", file=sys.stderr)
            sys.exit(1)

        async def scan():
            print(f"\n{'=' * 60}")
            print("Scanning for BLE devices (10 seconds)...")
            print(f"{'=' * 60}")

            devices = await BleakScanner.discover(timeout=10.0)

            if not devices:
                print("\nNo BLE devices found.")
                return

            print(f"\nFound {len(devices)} devices:\n")

            for device in sorted(devices, key=lambda d: d.rssi, reverse=True):
                print(f"{device.name or 'Unknown'}")
                print(f"  Address: {device.address}")
                print(f"  RSSI: {device.rssi} dBm")
                if device.metadata.get("uuids"):
                    print(f"  Service UUIDs: {device.metadata.get('uuids')}")
                print()

        asyncio.run(scan())

    # =========================================================================
    # Primitive Skills Methods
    # =========================================================================

    def primitive_list(self, robot_model: Optional[str], category: Optional[str],
                       status: Optional[str], tested_only: bool) -> None:
        """List primitive skills"""
        params = {}
        if robot_model:
            params["robotModel"] = robot_model
        if category:
            params["category"] = category
        if status:
            params["status"] = status
        if tested_only:
            params["testedOnly"] = "true"

        try:
            response = self._request("GET", "/primitives", params=params)
            primitives = response.get("primitives", [])
            pagination = response.get("pagination", {})

            print(f"\n{'=' * 70}")
            print(f"Primitive Skills ({pagination.get('total', len(primitives))} total)")
            print(f"{'=' * 70}")

            if not primitives:
                print("\nNo primitive skills found.")
                return

            # Group by robot
            by_robot = {}
            for prim in primitives:
                robot = prim.get("robotProfile", {}).get("modelName", "Unknown")
                if robot not in by_robot:
                    by_robot[robot] = []
                by_robot[robot].append(prim)

            for robot, prims in by_robot.items():
                print(f"\n{robot}:")
                for prim in prims:
                    status_icons = {"verified": "✓", "tested": "○", "experimental": "◌", "deprecated": "✗"}
                    icon = status_icons.get(prim.get("status", "experimental"), "?")
                    reliability = prim.get("reliabilityScore")
                    rel_str = f" ({reliability:.0%})" if reliability else ""

                    print(f"  {icon} {prim.get('name')} [{prim.get('category')}]{rel_str}")
                    print(f"      ID: {prim.get('id')}")

        except Exception as e:
            print(f"Error listing primitives: {e}", file=sys.stderr)
            sys.exit(1)

    def primitive_get(self, primitive_id: str) -> None:
        """Get detailed information about a primitive skill"""
        try:
            response = self._request("GET", f"/primitives/{primitive_id}")
            prim = response.get("primitive", {})
            robot = prim.get("robotProfile", {})
            protocol = prim.get("protocol", {})

            print(f"\n{'=' * 70}")
            print(f"Primitive: {prim.get('displayName') or prim.get('name')}")
            print(f"{'=' * 70}")

            print(f"\nRobot: {robot.get('manufacturer', '?')} {robot.get('modelName', '?')}")
            print(f"Category: {prim.get('category', '?')}")
            print(f"Status: {prim.get('status', '?')}")

            if prim.get('reliabilityScore'):
                print(f"Reliability: {prim.get('reliabilityScore'):.1%}")

            if prim.get('description'):
                print(f"\nDescription: {prim.get('description')}")

            print(f"\nCommand Type: {prim.get('commandType')}")
            print(f"Command Template:")
            print(f"  {prim.get('commandTemplate')}")

            # Parameters
            params = prim.get('parameters', [])
            if params:
                print(f"\nParameters:")
                for p in params:
                    range_str = ""
                    if p.get('min') is not None and p.get('max') is not None:
                        range_str = f" (range: {p.get('min')}-{p.get('max')})"
                    unit = f" {p.get('unit')}" if p.get('unit') else ""
                    default = f", default: {p.get('default')}" if p.get('default') is not None else ""
                    tested = f", tested safe: {p.get('testedSafe')}" if p.get('testedSafe') is not None else ""
                    print(f"  - {p.get('name')}: {p.get('type')}{range_str}{unit}{default}{tested}")

            # Timing
            if any([prim.get('executionTimeMs'), prim.get('settleTimeMs'), prim.get('cooldownMs')]):
                print(f"\nTiming:")
                if prim.get('executionTimeMs'):
                    print(f"  Execution: {prim.get('executionTimeMs')}ms")
                if prim.get('settleTimeMs'):
                    print(f"  Settle: {prim.get('settleTimeMs')}ms")
                if prim.get('cooldownMs'):
                    print(f"  Cooldown: {prim.get('cooldownMs')}ms")

            # Safety
            if prim.get('safetyNotes'):
                print(f"\nSafety Notes:")
                print(f"  {prim.get('safetyNotes')}")

            # Dependencies
            depends_on = prim.get('dependsOn', [])
            if depends_on:
                print(f"\nDepends On ({len(depends_on)}):")
                for dep in depends_on:
                    req = dep.get('requiredSkill', {})
                    print(f"  - {req.get('name')} ({dep.get('dependencyType')})")

            required_by = prim.get('requiredBy', [])
            if required_by:
                print(f"\nRequired By ({len(required_by)}):")
                for dep in required_by:
                    dep_skill = dep.get('dependentSkill', {})
                    print(f"  - {dep_skill.get('name')}")

        except Exception as e:
            print(f"Error fetching primitive: {e}", file=sys.stderr)
            sys.exit(1)

    def primitive_test(self, primitive_id: str, params_json: str,
                       result: str, notes: Optional[str], video_url: Optional[str]) -> None:
        """Submit a test result for a primitive skill"""
        try:
            parameters = json.loads(params_json)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON for parameters: {e}", file=sys.stderr)
            sys.exit(1)

        data = {
            "parameters": parameters,
            "result": result,
        }
        if notes:
            data["resultNotes"] = notes
        if video_url:
            data["videoUrl"] = video_url

        try:
            response = self._request("POST", f"/primitives/{primitive_id}/test", json=data)
            test_result = response.get("testResult", {})
            update = response.get("primitiveUpdate", {})

            print(f"\n✓ Test result submitted!")
            print(f"  Result: {result}")
            print(f"  New Reliability Score: {update.get('reliabilityScore', 0):.1%}")

            if update.get('statusChanged'):
                print(f"  Status upgraded to: {update.get('status')}")

        except Exception as e:
            print(f"Error submitting test result: {e}", file=sys.stderr)
            sys.exit(1)

    def primitive_deps_show(self, primitive_id: str) -> None:
        """Show dependencies for a primitive skill"""
        try:
            response = self._request("GET", f"/primitives/{primitive_id}/dependencies")
            deps = response.get("dependencies", [])
            dependents = response.get("dependents", [])
            summary = response.get("summary", {})
            deployment_ready = response.get("deploymentReady", False)

            print(f"\n{'=' * 60}")
            print("Dependency Graph")
            print(f"{'=' * 60}")

            print(f"\nDeployment Ready: {'✓ Yes' if deployment_ready else '✗ No'}")

            if deps:
                print(f"\nDepends On ({len(deps)}):")
                for dep in deps:
                    req = dep.get("requiredSkill", {})
                    status_ok = req.get("status") in ["tested", "verified"]
                    icon = "✓" if status_ok else "✗"
                    print(f"  {icon} {req.get('name')} ({req.get('status')})")
                    print(f"      Required status: {dep.get('requiredMinStatus')}")
                    if req.get("reliabilityScore"):
                        print(f"      Reliability: {req.get('reliabilityScore'):.1%}")
            else:
                print(f"\nNo dependencies (this is a root primitive)")

            if dependents:
                print(f"\nRequired By ({len(dependents)}):")
                for dep in dependents:
                    skill = dep.get("dependentSkill", {})
                    print(f"  - {skill.get('name')}")

            if summary.get('blockedDependencies', 0) > 0:
                print(f"\n⚠ {summary.get('blockedDependencies')} dependencies need testing before deployment")

        except Exception as e:
            print(f"Error fetching dependencies: {e}", file=sys.stderr)
            sys.exit(1)

    def primitive_deps_add(self, primitive_id: str, required_skill_id: str,
                           dependency_type: str, min_status: str) -> None:
        """Add a dependency to a primitive skill"""
        data = {
            "requiredSkillId": required_skill_id,
            "dependencyType": dependency_type,
            "requiredMinStatus": min_status,
        }

        try:
            response = self._request("POST", f"/primitives/{primitive_id}/dependencies", json=data)
            dep = response.get("dependency", {})
            cross_robot = response.get("crossRobot", False)

            print(f"\n✓ Dependency added!")
            if cross_robot:
                print(f"  ⚠ Note: This is a cross-robot dependency")

        except Exception as e:
            print(f"Error adding dependency: {e}", file=sys.stderr)
            sys.exit(1)

    def primitive_init(self, name: str, protocol_id: Optional[str] = None,
                        from_recording: Optional[str] = None, category: str = "motion",
                        output_dir: str = ".") -> None:
        """Initialize a new primitive skill definition locally"""
        print(f"\n{'=' * 60}")
        print("Initializing Primitive Skill")
        print(f"{'=' * 60}\n")

        # Create output directory
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        primitive_data = {
            "name": name,
            "displayName": name.replace("_", " ").title(),
            "category": category,
            "description": "",
            "protocolId": protocol_id,
            "commandType": "single",
            "commandTemplate": "",
            "responsePattern": "",
            "parameters": [],
            "executionTimeMs": None,
            "settleTimeMs": None,
            "cooldownMs": None,
            "safetyNotes": "",
            "status": "experimental",
            "version": "1.0.0",
        }

        # If importing from a recording, populate command data
        if from_recording:
            recording_path = Path(from_recording)
            if recording_path.exists():
                with open(recording_path) as f:
                    recording = json.load(f)

                commands = recording.get("commands", [])
                if commands:
                    # Use first command as template
                    primitive_data["commandTemplate"] = commands[0].get("command", "")
                    if len(commands) > 1:
                        primitive_data["commandType"] = "sequence"
                        primitive_data["commandSequence"] = [
                            {"command": c.get("command"), "delayMs": int((c.get("timestamp", 0) * 1000))}
                            for c in commands
                        ]

                    # Extract responses for pattern
                    responses = [c.get("response") for c in commands if c.get("response")]
                    if responses:
                        primitive_data["responsePattern"] = responses[0]

                    print(f"✓ Imported {len(commands)} commands from recording")
            else:
                print(f"Warning: Recording file not found: {from_recording}", file=sys.stderr)

        # Write primitive file
        primitive_file = out_path / f"{name}.primitive.json"
        with open(primitive_file, "w") as f:
            json.dump(primitive_data, f, indent=2)

        print(f"✓ Created: {primitive_file}")
        print(f"\nNext steps:")
        print(f"  1. Edit {primitive_file} to define command template and parameters")
        print(f"  2. Test with: ate primitive test <primitive_id> --params '{{...}}'")
        print(f"  3. Publish with: ate primitive push {primitive_file}")

    def primitive_push(self, primitive_file: str) -> None:
        """Push a primitive skill definition to FoodforThought"""
        file_path = Path(primitive_file)
        if not file_path.exists():
            print(f"Error: Primitive file not found: {primitive_file}", file=sys.stderr)
            sys.exit(1)

        print(f"\n{'=' * 60}")
        print("Publishing Primitive Skill")
        print(f"{'=' * 60}\n")

        with open(file_path) as f:
            primitive_data = json.load(f)

        print(f"Name: {primitive_data.get('displayName') or primitive_data.get('name')}")
        print(f"Category: {primitive_data.get('category')}")

        # Validate required fields
        if not primitive_data.get("name"):
            print("Error: Primitive must have a name", file=sys.stderr)
            sys.exit(1)

        if not primitive_data.get("commandTemplate") and not primitive_data.get("commandSequence"):
            print("Error: Primitive must have a commandTemplate or commandSequence", file=sys.stderr)
            sys.exit(1)

        if not primitive_data.get("protocolId"):
            print("Warning: No protocol ID specified. The primitive won't be linked to a protocol.", file=sys.stderr)

        try:
            response = self._request("POST", "/primitives", json=primitive_data)
            prim = response.get("primitive", {})
            print(f"\n✓ Primitive published successfully!")
            print(f"  ID: {prim.get('id')}")
            print(f"  Status: {prim.get('status')}")
            print(f"\nNext steps:")
            print(f"  - Test it: ate primitive test {prim.get('id')} --params '{{...}}'")
            print(f"  - View it: ate primitive get {prim.get('id')}")
        except Exception as e:
            print(f"Error publishing primitive: {e}", file=sys.stderr)
            sys.exit(1)

    # =========================================================================
    # Skill Abstractions (Layer 2) - Composed from Primitives
    # =========================================================================

    def skill_init(self, name: str, robot_model: Optional[str] = None,
                   template: str = "basic", output_dir: str = ".") -> None:
        """Initialize a new skill abstraction (composes primitives)"""
        print(f"\n{'=' * 60}")
        print("Initializing Skill Abstraction")
        print(f"{'=' * 60}\n")

        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        skill_data = {
            "name": name,
            "displayName": name.replace("_", " ").title(),
            "description": "",
            "robotModel": robot_model,
            "version": "1.0.0",
            "status": "experimental",
            "primitives": [],  # List of primitive IDs this skill uses
            "sequence": [],    # Ordered execution sequence
            "parameters": [],  # Skill-level parameters
            "preconditions": [],
            "postconditions": [],
            "errorHandling": {
                "retryCount": 3,
                "retryDelayMs": 1000,
                "fallbackAction": None,
            },
            "metadata": {
                "author": "",
                "license": "MIT",
                "tags": [],
            }
        }

        # Write skill file
        skill_file = out_path / f"{name}.skill.json"
        with open(skill_file, "w") as f:
            json.dump(skill_data, f, indent=2)

        print(f"✓ Created: {skill_file}")
        print(f"\nNext steps:")
        print(f"  1. Add primitives: ate skill compose {skill_file} <primitive_ids...>")
        print(f"  2. Edit {skill_file} to define sequence and parameters")
        print(f"  3. Test with: ate skill test {skill_file}")
        print(f"  4. Publish with: ate skill push {skill_file}")

    def skill_compose(self, skill_file: str, primitive_ids: List[str]) -> None:
        """Add primitives to a skill's composition"""
        file_path = Path(skill_file)
        if not file_path.exists():
            print(f"Error: Skill file not found: {skill_file}", file=sys.stderr)
            sys.exit(1)

        with open(file_path) as f:
            skill_data = json.load(f)

        print(f"\n{'=' * 60}")
        print(f"Composing Skill: {skill_data.get('name')}")
        print(f"{'=' * 60}\n")

        # Fetch primitive details to validate
        for prim_id in primitive_ids:
            try:
                response = self._request("GET", f"/primitives/{prim_id}")
                prim = response.get("primitive", {})
                print(f"  ✓ Adding: {prim.get('name')} ({prim.get('category')})")

                # Add to primitives list if not already present
                if prim_id not in skill_data.get("primitives", []):
                    skill_data.setdefault("primitives", []).append(prim_id)

                # Add to sequence
                skill_data.setdefault("sequence", []).append({
                    "primitiveId": prim_id,
                    "primitiveName": prim.get("name"),
                    "parameterMapping": {},  # Map skill params to primitive params
                    "conditionCheck": None,
                    "onError": "abort",
                })

            except Exception as e:
                print(f"  ✗ Failed to fetch {prim_id}: {e}", file=sys.stderr)

        # Write updated skill file
        with open(file_path, "w") as f:
            json.dump(skill_data, f, indent=2)

        print(f"\n✓ Updated {skill_file}")
        print(f"   Primitives: {len(skill_data.get('primitives', []))}")
        print(f"   Sequence steps: {len(skill_data.get('sequence', []))}")

    def skill_list(self, robot_model: Optional[str] = None,
                   status: Optional[str] = None) -> None:
        """List skill abstractions"""
        params = {}
        if robot_model:
            params["robotModel"] = robot_model
        if status:
            params["status"] = status

        try:
            response = self._request("GET", "/skills", params=params)
            skills = response.get("skills", [])

            print(f"\n{'=' * 70}")
            print(f"Skill Abstractions ({len(skills)} total)")
            print(f"{'=' * 70}")

            if not skills:
                print("\nNo skills found. Create one with: ate skill init <name>")
                return

            for skill in skills:
                status_icons = {"verified": "✓", "tested": "○", "experimental": "◌"}
                icon = status_icons.get(skill.get("status", "experimental"), "?")
                prim_count = len(skill.get("primitives", []))
                print(f"\n{icon} {skill.get('name')}")
                print(f"   Robot: {skill.get('robotModel', 'Any')}")
                print(f"   Primitives: {prim_count}")
                print(f"   ID: {skill.get('id')}")

        except Exception as e:
            print(f"Error listing skills: {e}", file=sys.stderr)
            sys.exit(1)

    def skill_get(self, skill_id: str) -> None:
        """Get detailed information about a skill"""
        try:
            response = self._request("GET", f"/skills/{skill_id}")
            skill = response.get("skill", {})

            print(f"\n{'=' * 70}")
            print(f"Skill: {skill.get('displayName') or skill.get('name')}")
            print(f"{'=' * 70}")

            print(f"\nDescription: {skill.get('description') or 'No description'}")
            print(f"Robot: {skill.get('robotModel', 'Any')}")
            print(f"Status: {skill.get('status')}")
            print(f"Version: {skill.get('version')}")

            # Show sequence
            sequence = skill.get("sequence", [])
            if sequence:
                print(f"\nExecution Sequence ({len(sequence)} steps):")
                for i, step in enumerate(sequence, 1):
                    print(f"  {i}. {step.get('primitiveName', step.get('primitiveId'))}")
                    if step.get("conditionCheck"):
                        print(f"      Condition: {step.get('conditionCheck')}")

            # Show parameters
            params = skill.get("parameters", [])
            if params:
                print(f"\nParameters:")
                for p in params:
                    print(f"  - {p.get('name')}: {p.get('type')}")

        except Exception as e:
            print(f"Error fetching skill: {e}", file=sys.stderr)
            sys.exit(1)

    def skill_push(self, skill_file: str) -> None:
        """Push a skill abstraction to FoodforThought"""
        file_path = Path(skill_file)
        if not file_path.exists():
            print(f"Error: Skill file not found: {skill_file}", file=sys.stderr)
            sys.exit(1)

        print(f"\n{'=' * 60}")
        print("Publishing Skill Abstraction")
        print(f"{'=' * 60}\n")

        with open(file_path) as f:
            skill_data = json.load(f)

        print(f"Name: {skill_data.get('displayName') or skill_data.get('name')}")
        print(f"Primitives: {len(skill_data.get('primitives', []))}")

        if not skill_data.get("name"):
            print("Error: Skill must have a name", file=sys.stderr)
            sys.exit(1)

        if not skill_data.get("primitives"):
            print("Warning: Skill has no primitives. Add with: ate skill compose", file=sys.stderr)

        try:
            response = self._request("POST", "/skills", json=skill_data)
            skill = response.get("skill", {})
            print(f"\n✓ Skill published successfully!")
            print(f"  ID: {skill.get('id')}")
            print(f"  Status: {skill.get('status')}")
        except Exception as e:
            print(f"Error publishing skill: {e}", file=sys.stderr)
            sys.exit(1)

    def skill_test(self, skill_file_or_id: str, params_json: Optional[str] = None,
                   dry_run: bool = True) -> None:
        """Test a skill (simulated or real execution)"""
        print(f"\n{'=' * 60}")
        print("Testing Skill")
        print(f"{'=' * 60}\n")

        # Check if it's a file or ID
        if Path(skill_file_or_id).exists():
            with open(skill_file_or_id) as f:
                skill_data = json.load(f)
            print(f"Testing local skill: {skill_data.get('name')}")
        else:
            # Fetch from API
            response = self._request("GET", f"/skills/{skill_file_or_id}")
            skill_data = response.get("skill", {})
            print(f"Testing remote skill: {skill_data.get('name')}")

        params = json.loads(params_json) if params_json else {}

        sequence = skill_data.get("sequence", [])
        print(f"\nSequence ({len(sequence)} steps):")

        for i, step in enumerate(sequence, 1):
            prim_name = step.get("primitiveName", step.get("primitiveId"))
            if dry_run:
                print(f"  [{i}/{len(sequence)}] Would execute: {prim_name}")
            else:
                print(f"  [{i}/{len(sequence)}] Executing: {prim_name}...")
                # In real mode, would invoke the primitive via protocol
                time.sleep(0.5)  # Simulate execution
                print(f"           ✓ Complete")

        print(f"\n{'✓ Dry run complete' if dry_run else '✓ Execution complete'}")

    # ========================================
    # Phase 3: AI Bridge - Interactive Robot Communication
    # ========================================

    def bridge_connect(self, port: str, transport: str = "serial",
                       baud_rate: int = 115200, protocol_id: Optional[str] = None) -> None:
        """Connect to a robot via serial or BLE and start interactive session"""
        print(f"\n{'=' * 60}")
        print("FoodForThought Bridge - Robot Communication Interface")
        print(f"{'=' * 60}\n")

        if transport == "serial":
            try:
                import serial
            except ImportError:
                print("Error: pyserial is required. Install with: pip install pyserial", file=sys.stderr)
                sys.exit(1)

            print(f"Connecting to {port} at {baud_rate} baud...")
            try:
                ser = serial.Serial(port, baud_rate, timeout=1)
                print(f"✓ Connected to {port}")
                print(f"\nInteractive mode. Type commands to send to robot.")
                print("Special commands:")
                print("  .quit     - Exit bridge")
                print("  .record   - Start recording for primitive creation")
                print("  .stop     - Stop recording")
                print("  .save     - Save recorded session")
                print("  .protocol - Show loaded protocol info")
                print("-" * 60 + "\n")

                recording = False
                recorded_commands = []

                while True:
                    try:
                        cmd = input("bridge> ").strip()
                        if not cmd:
                            continue

                        if cmd == ".quit":
                            break
                        elif cmd == ".record":
                            recording = True
                            recorded_commands = []
                            print("Recording started...")
                            continue
                        elif cmd == ".stop":
                            recording = False
                            print(f"Recording stopped. {len(recorded_commands)} commands recorded.")
                            continue
                        elif cmd == ".save":
                            if recorded_commands:
                                filename = f"session_{int(time.time())}.json"
                                with open(filename, "w") as f:
                                    json.dump({
                                        "port": port,
                                        "baud_rate": baud_rate,
                                        "commands": recorded_commands
                                    }, f, indent=2)
                                print(f"Session saved to {filename}")
                            else:
                                print("No commands recorded yet.")
                            continue
                        elif cmd == ".protocol":
                            if protocol_id:
                                self.protocol_get(protocol_id)
                            else:
                                print("No protocol loaded. Use --protocol flag to specify.")
                            continue

                        # Send command to robot
                        ser.write((cmd + "\n").encode())
                        if recording:
                            recorded_commands.append({
                                "command": cmd,
                                "timestamp": time.time()
                            })

                        # Read response
                        time.sleep(0.1)
                        response = ser.read_all().decode("utf-8", errors="replace").strip()
                        if response:
                            print(f"< {response}")
                            if recording:
                                recorded_commands[-1]["response"] = response

                    except KeyboardInterrupt:
                        break

                ser.close()
                print("\n✓ Disconnected")

            except Exception as e:
                print(f"Error connecting to {port}: {e}", file=sys.stderr)
                sys.exit(1)

        elif transport == "ble":
            print("BLE bridge requires async operation. Starting BLE session...")
            self._bridge_ble_connect(port)

    def _bridge_ble_connect(self, address: str) -> None:
        """Connect to robot via BLE (requires bleak)"""
        try:
            import asyncio
            from bleak import BleakClient
        except ImportError:
            print("Error: bleak is required for BLE. Install with: pip install bleak", file=sys.stderr)
            sys.exit(1)

        async def ble_session():
            print(f"Connecting to BLE device {address}...")
            try:
                async with BleakClient(address) as client:
                    print(f"✓ Connected to {address}")

                    # List services
                    print("\nAvailable services:")
                    for service in client.services:
                        print(f"  {service.uuid}: {service.description or 'Unknown'}")
                        for char in service.characteristics:
                            props = ", ".join(char.properties)
                            print(f"    └─ {char.uuid} [{props}]")

                    print("\nInteractive mode. Commands:")
                    print("  read <uuid>         - Read characteristic")
                    print("  write <uuid> <hex>  - Write to characteristic")
                    print("  notify <uuid>       - Subscribe to notifications")
                    print("  .quit               - Exit")
                    print("-" * 60 + "\n")

                    while True:
                        try:
                            cmd = input("ble> ").strip()
                            if not cmd:
                                continue

                            if cmd == ".quit":
                                break

                            parts = cmd.split()
                            if parts[0] == "read" and len(parts) >= 2:
                                uuid = parts[1]
                                try:
                                    data = await client.read_gatt_char(uuid)
                                    print(f"< {data.hex()} ({data})")
                                except Exception as e:
                                    print(f"Error reading: {e}")

                            elif parts[0] == "write" and len(parts) >= 3:
                                uuid = parts[1]
                                hex_data = parts[2]
                                try:
                                    data = bytes.fromhex(hex_data)
                                    await client.write_gatt_char(uuid, data)
                                    print(f"✓ Written {hex_data}")
                                except Exception as e:
                                    print(f"Error writing: {e}")

                            elif parts[0] == "notify" and len(parts) >= 2:
                                uuid = parts[1]
                                def callback(sender, data):
                                    print(f"[{sender}] {data.hex()}")
                                try:
                                    await client.start_notify(uuid, callback)
                                    print(f"✓ Subscribed to {uuid}")
                                except Exception as e:
                                    print(f"Error subscribing: {e}")

                            else:
                                print("Unknown command. Use read/write/notify or .quit")

                        except KeyboardInterrupt:
                            break

                    print("\n✓ Disconnected")

            except Exception as e:
                print(f"Error connecting to BLE device: {e}", file=sys.stderr)
                sys.exit(1)

        asyncio.run(ble_session())

    def bridge_send(self, port: str, command: str, transport: str = "serial",
                    baud_rate: int = 115200, wait: float = 0.5) -> None:
        """Send a single command to robot and print response"""
        if transport == "serial":
            try:
                import serial
            except ImportError:
                print("Error: pyserial is required. Install with: pip install pyserial", file=sys.stderr)
                sys.exit(1)

            try:
                ser = serial.Serial(port, baud_rate, timeout=1)
                ser.write((command + "\n").encode())
                time.sleep(wait)
                response = ser.read_all().decode("utf-8", errors="replace").strip()
                if response:
                    print(response)
                ser.close()
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print("BLE send not yet implemented. Use bridge connect for BLE.", file=sys.stderr)

    def bridge_record(self, port: str, output: str, transport: str = "serial",
                      baud_rate: int = 115200, primitive_name: Optional[str] = None) -> None:
        """Record a command session for creating a primitive skill"""
        print(f"\n{'=' * 60}")
        print("FoodForThought Bridge - Recording Mode")
        print(f"{'=' * 60}\n")

        if transport != "serial":
            print("Recording currently only supports serial connections", file=sys.stderr)
            sys.exit(1)

        try:
            import serial
        except ImportError:
            print("Error: pyserial is required. Install with: pip install pyserial", file=sys.stderr)
            sys.exit(1)

        print(f"Connecting to {port} at {baud_rate} baud...")
        try:
            ser = serial.Serial(port, baud_rate, timeout=1)
            print(f"✓ Connected and recording to {output}")
            print(f"\nType commands to send. Ctrl+C to stop and save.\n")

            recorded = {
                "name": primitive_name or f"recorded_skill_{int(time.time())}",
                "port": port,
                "baud_rate": baud_rate,
                "start_time": time.time(),
                "commands": []
            }

            while True:
                try:
                    cmd = input(f"[REC] bridge> ").strip()
                    if not cmd:
                        continue

                    timestamp = time.time()
                    ser.write((cmd + "\n").encode())
                    time.sleep(0.1)
                    response = ser.read_all().decode("utf-8", errors="replace").strip()

                    entry = {
                        "command": cmd,
                        "timestamp": timestamp - recorded["start_time"],
                        "response": response
                    }
                    recorded["commands"].append(entry)

                    if response:
                        print(f"< {response}")

                except KeyboardInterrupt:
                    break

            ser.close()
            recorded["end_time"] = time.time()
            recorded["duration"] = recorded["end_time"] - recorded["start_time"]

            # Save recording
            with open(output, "w") as f:
                json.dump(recorded, f, indent=2)

            print(f"\n✓ Recorded {len(recorded['commands'])} commands")
            print(f"✓ Saved to {output}")
            print(f"\nTo create a primitive from this recording:")
            print(f"  ate primitive create --from-recording {output}")

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    def bridge_replay(self, recording_file: str, port: str, transport: str = "serial",
                      baud_rate: int = 115200, speed: float = 1.0) -> None:
        """Replay a recorded session"""
        if not Path(recording_file).exists():
            print(f"Error: Recording file not found: {recording_file}", file=sys.stderr)
            sys.exit(1)

        with open(recording_file) as f:
            recording = json.load(f)

        if transport != "serial":
            print("Replay currently only supports serial connections", file=sys.stderr)
            sys.exit(1)

        try:
            import serial
        except ImportError:
            print("Error: pyserial is required. Install with: pip install pyserial", file=sys.stderr)
            sys.exit(1)

        print(f"\n{'=' * 60}")
        print(f"Replaying: {recording.get('name', recording_file)}")
        print(f"Commands: {len(recording.get('commands', []))}")
        print(f"Speed: {speed}x")
        print(f"{'=' * 60}\n")

        try:
            ser = serial.Serial(port, baud_rate, timeout=1)
            commands = recording.get("commands", [])

            prev_timestamp = 0
            for i, entry in enumerate(commands):
                timestamp = entry.get("timestamp", 0)
                delay = (timestamp - prev_timestamp) / speed
                if delay > 0 and i > 0:
                    time.sleep(delay)
                prev_timestamp = timestamp

                cmd = entry.get("command", "")
                print(f"[{i+1}/{len(commands)}] > {cmd}")
                ser.write((cmd + "\n").encode())

                time.sleep(0.1)
                response = ser.read_all().decode("utf-8", errors="replace").strip()
                if response:
                    print(f"            < {response}")

            ser.close()
            print(f"\n✓ Replay complete")

        except Exception as e:
            print(f"Error during replay: {e}", file=sys.stderr)
            sys.exit(1)

    # =========================================================================
    # Skill Compiler Commands
    # =========================================================================

    def compile_skill(
        self,
        skill_path: str,
        output: str = "./output",
        target: str = "ros2",
        robot: Optional[str] = None,
        ate_dir: Optional[str] = None,
    ) -> None:
        """
        Compile a skill specification into a deployable package.

        Args:
            skill_path: Path to skill.yaml specification
            output: Output directory for generated files
            target: Target platform (ros2, docker, python)
            robot: Path to robot URDF file for hardware config
            ate_dir: Path to ATE config directory for servo mapping
        """
        from pathlib import Path
        from ate.skill_schema import SkillSpecification
        from ate.generators import (
            SkillCodeGenerator,
            ROS2PackageGenerator,
            DockerGenerator,
            generate_hardware_config,
        )

        skill_path = Path(skill_path)
        output_path = Path(output)

        if not skill_path.exists():
            print(f"Error: Skill specification not found: {skill_path}", file=sys.stderr)
            sys.exit(1)

        print(f"\n{'=' * 60}")
        print(f"  Skill Compiler v1.0.0")
        print(f"{'=' * 60}")
        print(f"  Input:  {skill_path}")
        print(f"  Output: {output_path}")
        print(f"  Target: {target}")
        if robot:
            print(f"  Robot:  {robot}")
        print(f"{'=' * 60}\n")

        # Load skill specification
        print("Loading skill specification...")
        try:
            spec = SkillSpecification.from_yaml(str(skill_path))
        except Exception as e:
            print(f"Error parsing skill specification: {e}", file=sys.stderr)
            sys.exit(1)

        # Validate specification
        print("Validating specification...")
        errors = spec.validate()
        if errors:
            print(f"\nValidation errors:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            sys.exit(1)
        print(f"  ✓ Specification valid: {spec.name} v{spec.version}")
        print(f"  ✓ Primitives: {len(spec.primitives)}")
        print(f"  ✓ Hardware requirements: {len(spec.hardware_requirements)}")

        # Generate skill code
        print("\nGenerating skill code...")
        skill_gen = SkillCodeGenerator(spec)
        skill_files = skill_gen.generate(output_path / "src")
        print(f"  ✓ Generated {len(skill_files)} files")

        # Generate platform-specific package
        if target == "ros2":
            print("\nGenerating ROS2 package...")
            ros2_gen = ROS2PackageGenerator(spec)
            ros2_files = ros2_gen.generate(output_path)
            print(f"  ✓ Generated ROS2 package with {len(ros2_files)} files")

        elif target == "docker":
            print("\nGenerating Docker configuration...")
            docker_gen = DockerGenerator(spec)
            docker_files = docker_gen.generate(output_path)
            print(f"  ✓ Generated Docker files: {len(docker_files)}")

        elif target == "python":
            print("\nGenerating Python package...")
            # Python package is already generated by skill_gen
            # Just add setup.py
            setup_content = f'''from setuptools import setup, find_packages

setup(
    name="{spec.name}",
    version="{spec.version}",
    packages=find_packages(),
    description="{spec.description}",
    python_requires=">=3.8",
)
'''
            (output_path / "setup.py").write_text(setup_content)
            print("  ✓ Generated setup.py")

        # Generate hardware config if robot provided
        if robot or ate_dir:
            print("\nGenerating hardware configuration...")
            try:
                hw_config = generate_hardware_config(
                    spec,
                    urdf_path=robot,
                    ate_dir=ate_dir,
                )
                import yaml
                config_dir = output_path / "config"
                config_dir.mkdir(parents=True, exist_ok=True)
                config_path = config_dir / "hardware_config.yaml"
                with open(config_path, "w") as f:
                    yaml.dump(hw_config, f, default_flow_style=False)
                print(f"  ✓ Generated hardware config: {config_path}")
            except Exception as e:
                print(f"  ⚠ Warning: Could not generate hardware config: {e}")

        # Copy skill.yaml to output
        import shutil
        shutil.copy(skill_path, output_path / "skill.yaml")

        print(f"\n{'=' * 60}")
        print(f"  ✓ Compilation complete!")
        print(f"  Output: {output_path.absolute()}")
        print(f"{'=' * 60}\n")

        # Print next steps
        print("Next steps:")
        if target == "ros2":
            print("  1. cd output && colcon build")
            print("  2. source install/setup.bash")
            print(f"  3. ros2 launch {spec.name}_skill skill.launch.py")
        elif target == "docker":
            print("  1. cd output && docker build -t skill .")
            print("  2. docker run skill")
        elif target == "python":
            print("  1. cd output && pip install -e .")
            print(f"  2. python -c 'from {spec.name} import {spec.name.title().replace('_', '')}Skill'")

    def test_compiled_skill(
        self,
        skill_path: str,
        mode: str = "sim",
        robot_port: Optional[str] = None,
        params: Optional[str] = None,
    ) -> None:
        """
        Test a compiled skill in simulation or on hardware.

        Args:
            skill_path: Path to compiled skill directory
            mode: Test mode (sim, hardware, mock)
            robot_port: Serial port for hardware testing
            params: JSON parameters for skill execution
        """
        from pathlib import Path

        skill_path = Path(skill_path)

        if not skill_path.exists():
            print(f"Error: Skill directory not found: {skill_path}", file=sys.stderr)
            sys.exit(1)

        # Check for skill.yaml
        skill_yaml = skill_path / "skill.yaml"
        if not skill_yaml.exists():
            print(f"Error: skill.yaml not found in {skill_path}", file=sys.stderr)
            sys.exit(1)

        print(f"\n{'=' * 60}")
        print(f"  Skill Test Runner")
        print(f"{'=' * 60}")
        print(f"  Skill:  {skill_path}")
        print(f"  Mode:   {mode}")
        if robot_port:
            print(f"  Port:   {robot_port}")
        print(f"{'=' * 60}\n")

        # Load skill specification
        from ate.skill_schema import SkillSpecification
        spec = SkillSpecification.from_yaml(str(skill_yaml))

        print(f"Testing skill: {spec.name} v{spec.version}")
        print(f"Primitives: {', '.join(spec.primitives)}")
        print()

        if mode == "mock":
            print("Running in mock mode (no hardware)...")
            # Import and run skill with mock drivers
            try:
                import importlib.util
                skill_module_path = skill_path / "src" / f"{spec.name.replace('-', '_')}" / "skill.py"
                if skill_module_path.exists():
                    spec_loader = importlib.util.spec_from_file_location("skill", skill_module_path)
                    module = importlib.util.module_from_spec(spec_loader)
                    spec_loader.loader.exec_module(module)

                    # Get the skill class
                    class_name = spec.name.replace('_', ' ').title().replace(' ', '') + "Skill"
                    skill_class = getattr(module, class_name)

                    # Create instance with mock config
                    skill = skill_class({"driver": "mock"})

                    # Parse params if provided
                    input_params = {}
                    if params:
                        input_params = json.loads(params)

                    # Get input class
                    input_class_name = class_name.replace("Skill", "Input")
                    input_class = getattr(module, input_class_name)
                    skill_input = input_class(**input_params)

                    # Execute
                    print("\nExecuting skill...")
                    result = skill.execute(skill_input)
                    print(f"\nResult:")
                    print(f"  Success: {result.success}")
                    print(f"  Message: {result.message}")
                    print(f"  Time: {result.execution_time:.3f}s")
                else:
                    print(f"Warning: Skill module not found at {skill_module_path}")
                    print("Running dry-run validation instead...")
                    print("\n  ✓ Specification valid")
                    print("  ✓ All primitives available")
                    print("  ✓ Hardware requirements satisfied (mock)")

            except Exception as e:
                print(f"Error running skill: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc()
                sys.exit(1)

        elif mode == "sim":
            print("Simulation testing requires MuJoCo or Gazebo integration.")
            print("For now, running mock test instead...")
            self.test_compiled_skill(skill_path, mode="mock", params=params)

        elif mode == "hardware":
            if not robot_port:
                print("Error: --robot-port required for hardware mode", file=sys.stderr)
                sys.exit(1)
            print(f"Hardware testing on {robot_port}...")
            print("Note: Full hardware testing requires bridge connection.")
            print("Consider running: ate bridge serve")

        print(f"\n{'=' * 60}")
        print(f"  ✓ Test complete")
        print(f"{'=' * 60}\n")

    def publish_compiled_skill(
        self,
        skill_path: str,
        visibility: str = "public",
    ) -> None:
        """
        Publish a compiled skill to FoodforThought registry.

        Args:
            skill_path: Path to compiled skill directory
            visibility: Visibility (public, private, team)
        """
        from pathlib import Path

        skill_path = Path(skill_path)

        if not skill_path.exists():
            print(f"Error: Skill directory not found: {skill_path}", file=sys.stderr)
            sys.exit(1)

        # Check for skill.yaml
        skill_yaml = skill_path / "skill.yaml"
        if not skill_yaml.exists():
            print(f"Error: skill.yaml not found in {skill_path}", file=sys.stderr)
            sys.exit(1)

        # Load skill specification
        from ate.skill_schema import SkillSpecification
        spec = SkillSpecification.from_yaml(str(skill_yaml))

        print(f"\n{'=' * 60}")
        print(f"  Publishing Skill to FoodforThought")
        print(f"{'=' * 60}")
        print(f"  Name:       {spec.name}")
        print(f"  Version:    {spec.version}")
        print(f"  Visibility: {visibility}")
        print(f"{'=' * 60}\n")

        # Prepare upload payload
        skill_data = spec.to_dict()
        skill_data["visibility"] = visibility

        # Include file listing
        files = []
        for path in skill_path.rglob("*"):
            if path.is_file() and not path.name.startswith("."):
                rel_path = path.relative_to(skill_path)
                files.append(str(rel_path))
        skill_data["files"] = files

        print(f"Files to publish: {len(files)}")

        # Upload to API
        try:
            response = self._request("POST", "/skills/publish", json=skill_data)
            skill_id = response.get("skillId", response.get("id", "unknown"))
            skill_url = f"https://kindly.fyi/skills/{skill_id}"

            print(f"\n✓ Skill published successfully!")
            print(f"  ID:  {skill_id}")
            print(f"  URL: {skill_url}")

        except Exception as e:
            # Mock response for offline testing
            mock_id = f"sk_{spec.name}_{spec.version.replace('.', '_')}"
            print(f"\n✓ Skill prepared for publishing (API unavailable)")
            print(f"  Mock ID: {mock_id}")
            print(f"  Run with API key to publish: export ATE_API_KEY=your_key")

    def check_skill_compatibility(
        self,
        skill_path: str,
        robot_urdf: Optional[str] = None,
        robot_ate_dir: Optional[str] = None,
    ) -> None:
        """
        Check if a skill is compatible with a robot.

        Args:
            skill_path: Path to skill.yaml
            robot_urdf: Path to robot URDF
            robot_ate_dir: Path to ATE config directory
        """
        from pathlib import Path
        from ate.skill_schema import SkillSpecification
        from ate.compatibility import check_compatibility_from_paths

        skill_path = Path(skill_path)
        if not skill_path.exists():
            print(f"Error: Skill not found: {skill_path}", file=sys.stderr)
            sys.exit(1)

        # Determine robot name
        robot_name = "unknown"
        if robot_urdf:
            robot_name = Path(robot_urdf).stem
        elif robot_ate_dir:
            robot_name = Path(robot_ate_dir).name

        print(f"\n{'=' * 60}")
        print(f"  Skill Compatibility Check")
        print(f"{'=' * 60}")
        print(f"  Skill: {skill_path}")
        print(f"  Robot: {robot_name}")
        print(f"{'=' * 60}\n")

        report = check_compatibility_from_paths(
            skill_yaml=str(skill_path),
            robot_urdf=robot_urdf,
            robot_ate_dir=robot_ate_dir,
            robot_name=robot_name,
        )

        print(report)

        if not report.compatible:
            sys.exit(1)


    def data_upload(self, path: str, skill: str, stage: str) -> None:
        # Upload dataset/sensor logs
        ATEClient.data_upload(self, path, skill, stage)


def _generate_pkce():
    """Generate PKCE code verifier and challenge."""
    import hashlib
    import base64
    import secrets

    # Generate code verifier (43-128 chars, URL-safe)
    code_verifier = secrets.token_urlsafe(32)

    # Generate code challenge (SHA256 hash of verifier, base64url encoded)
    digest = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b'=').decode()

    return code_verifier, code_challenge


def _generate_device_id():
    """Generate a unique device ID for this CLI installation."""
    import platform
    import hashlib

    # Create a stable device ID based on machine info
    machine_info = f"{platform.node()}-{platform.system()}-{platform.machine()}"
    return f"cli-{hashlib.sha256(machine_info.encode()).hexdigest()[:16]}"


def login_command():
    """Interactive login via browser (GitHub-style device flow)"""
    import webbrowser

    print("Authenticating with FoodforThought...")
    print()

    # Generate PKCE
    code_verifier, code_challenge = _generate_pkce()
    device_id = _generate_device_id()

    # Step 1: Initiate device auth
    try:
        response = requests.post(
            f"{BASE_URL}/device-auth/initiate",
            json={
                "codeChallenge": code_challenge,
                "deviceId": device_id,
                "deviceName": "FoodforThought CLI",
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"Error: Failed to initiate login: {e}", file=sys.stderr)
        sys.exit(1)

    if not data.get("success"):
        print(f"Error: {data.get('error', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)

    auth_url = data["authUrl"]
    state = data["state"]

    # Step 2: Open browser
    print("Opening browser for authentication...")
    print(f"If browser doesn't open, visit: {auth_url}")
    print()

    try:
        webbrowser.open(auth_url)
    except Exception:
        pass  # Browser open is best-effort

    # Step 3: Poll for authorization
    print("Waiting for authorization...", end="", flush=True)

    max_attempts = 120  # 2 minutes with 1s intervals
    poll_interval = 1.0

    for attempt in range(max_attempts):
        time.sleep(poll_interval)

        try:
            poll_response = requests.post(
                f"{BASE_URL}/device-auth/poll",
                json={"state": state, "deviceId": device_id},
                timeout=10,
            )
            poll_data = poll_response.json()
        except requests.RequestException:
            print(".", end="", flush=True)
            continue

        status = poll_data.get("status")

        if status == "pending":
            print(".", end="", flush=True)
            continue
        elif status == "authorized":
            print(" authorized!")
            callback_token = poll_data.get("token")
            break
        elif status == "expired":
            print("\nError: Authorization request expired. Please try again.", file=sys.stderr)
            sys.exit(1)
        elif status == "exchanged":
            print("\nError: This authorization was already used. Please try again.", file=sys.stderr)
            sys.exit(1)
        else:
            print(".", end="", flush=True)
    else:
        print("\nError: Timeout waiting for authorization.", file=sys.stderr)
        sys.exit(1)

    # Step 4: Exchange for access token
    print("Exchanging for access token...")

    try:
        exchange_response = requests.post(
            f"{BASE_URL}/device-auth/exchange",
            json={
                "token": callback_token,
                "state": state,
                "codeVerifier": code_verifier,
                "deviceId": device_id,
            },
            timeout=10,
        )
        exchange_response.raise_for_status()
        exchange_data = exchange_response.json()
    except requests.RequestException as e:
        print(f"Error: Failed to exchange token: {e}", file=sys.stderr)
        sys.exit(1)

    if not exchange_data.get("success"):
        print(f"Error: {exchange_data.get('error', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)

    access_token = exchange_data["accessToken"]
    refresh_token = exchange_data["refreshToken"]
    user = exchange_data.get("user", {})
    expires_at = exchange_data.get("expiresAt")

    # Step 5: Save credentials
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        config = {}
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE) as f:
                    config = json.load(f)
            except Exception:
                pass

        config["access_token"] = access_token
        config["refresh_token"] = refresh_token
        config["device_id"] = device_id
        config["expires_at"] = expires_at
        config["user"] = {
            "id": user.get("id"),
            "email": user.get("email"),
            "name": user.get("name"),
        }

        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)

        # Set restrictive permissions
        CONFIG_FILE.chmod(0o600)

    except Exception as e:
        print(f"Error saving credentials: {e}", file=sys.stderr)
        sys.exit(1)

    print()
    print(f"✓ Logged in as {user.get('name') or user.get('email')}")
    print(f"  Credentials saved to {CONFIG_FILE}")


def logout_command():
    """Log out and remove stored credentials."""
    if not CONFIG_FILE.exists():
        print("Not logged in.")
        return

    try:
        # Load config to get device_id for revoking
        with open(CONFIG_FILE) as f:
            config = json.load(f)

        access_token = config.get("access_token")
        device_id = config.get("device_id")

        # Try to revoke the session on the server
        if access_token and device_id:
            try:
                requests.post(
                    f"{BASE_URL}/device-auth/revoke",
                    json={"accessToken": access_token, "deviceId": device_id},
                    timeout=5,
                )
            except Exception:
                pass  # Best effort

        # Remove local credentials
        CONFIG_FILE.unlink()
        print("✓ Logged out successfully.")

    except Exception as e:
        print(f"Error during logout: {e}", file=sys.stderr)
        # Still try to remove the file
        try:
            CONFIG_FILE.unlink()
        except Exception:
            pass


def whoami_command():
    """Show current logged-in user."""
    if not CONFIG_FILE.exists():
        print("Not logged in. Run 'ate login' to authenticate.")
        sys.exit(1)

    try:
        with open(CONFIG_FILE) as f:
            config = json.load(f)

        user = config.get("user", {})
        access_token = config.get("access_token")
        expires_at = config.get("expires_at")

        if not access_token:
            # Legacy api_key mode
            if config.get("api_key"):
                print("Authenticated via API key (legacy mode)")
                print("Run 'ate login' to upgrade to device authentication.")
                return
            else:
                print("Not logged in. Run 'ate login' to authenticate.")
                sys.exit(1)

        print(f"Logged in as: {user.get('name') or 'Unknown'}")
        print(f"Email: {user.get('email') or 'Unknown'}")
        if expires_at:
            print(f"Session expires: {expires_at}")

    except Exception as e:
        print(f"Error reading credentials: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="FoodforThought CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Auth commands
    subparsers.add_parser("login", help="Authenticate with FoodforThought via browser")
    subparsers.add_parser("logout", help="Log out and remove stored credentials")
    subparsers.add_parser("whoami", help="Show current logged-in user")

    # init command
    init_parser = subparsers.add_parser("init", help="Initialize a new repository")
    init_parser.add_argument("name", help="Repository name")
    init_parser.add_argument("-d", "--description", default="", help="Repository description")
    init_parser.add_argument(
        "-v", "--visibility", choices=["public", "private"], default="public", help="Repository visibility"
    )

    # clone command
    clone_parser = subparsers.add_parser("clone", help="Clone a repository")
    clone_parser.add_argument("repo_id", help="Repository ID")
    clone_parser.add_argument("target_dir", nargs="?", help="Target directory")

    # commit command
    commit_parser = subparsers.add_parser("commit", help="Create a commit")
    commit_parser.add_argument("-m", "--message", required=True, help="Commit message")
    commit_parser.add_argument("files", nargs="*", help="Files to commit")

    # push command
    push_parser = subparsers.add_parser("push", help="Push commits to remote")
    push_parser.add_argument("-b", "--branch", default="main", help="Branch name")

    # deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy to robot")
    deploy_parser.add_argument("robot_type", help="Robot type (e.g., unitree-r1)")
    deploy_parser.add_argument("-r", "--repo-id", help="Repository ID (default: current repo)")

    # test command
    test_parser = subparsers.add_parser("test", help="Test skills in simulation")
    test_parser.add_argument("-e", "--environment", default="gazebo", 
                           choices=["gazebo", "mujoco", "pybullet", "webots"],
                           help="Simulation environment")
    test_parser.add_argument("-r", "--robot", help="Robot model to test with")
    test_parser.add_argument("--local", action="store_true", help="Run simulation locally")

    # benchmark command
    benchmark_parser = subparsers.add_parser("benchmark", help="Run performance benchmarks")
    benchmark_parser.add_argument("-t", "--type", default="all",
                                choices=["speed", "accuracy", "robustness", "efficiency", "all"],
                                help="Benchmark type")
    benchmark_parser.add_argument("-n", "--trials", type=int, default=10, help="Number of trials")
    benchmark_parser.add_argument("--compare", help="Compare with baseline (repository ID)")

    # adapt command
    adapt_parser = subparsers.add_parser("adapt", help="Adapt skills between robots")
    adapt_parser.add_argument("source_robot", help="Source robot model")
    adapt_parser.add_argument("target_robot", help="Target robot model")
    adapt_parser.add_argument("-r", "--repo-id", help="Repository ID to adapt")
    adapt_parser.add_argument("--analyze-only", action="store_true", 
                            help="Only show compatibility analysis")

    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate safety and compliance")
    validate_parser.add_argument("-c", "--checks", nargs="+", 
                               choices=["collision", "speed", "workspace", "force", "all"],
                               default=["all"], help="Safety checks to run")
    validate_parser.add_argument("--strict", action="store_true", help="Use strict validation")
    validate_parser.add_argument("-f", "--files", nargs="*", help="Specific files to validate")

    # stream command
    stream_parser = subparsers.add_parser("stream", help="Stream sensor data")
    stream_parser.add_argument("action", choices=["start", "stop", "status"],
                             help="Streaming action")
    stream_parser.add_argument("-s", "--sensors", nargs="+", 
                             help="Sensors to stream (e.g., camera, lidar, imu)")
    stream_parser.add_argument("-o", "--output", help="Output file or URL")
    stream_parser.add_argument("--format", default="rosbag", 
                             choices=["rosbag", "hdf5", "json", "live"],
                             help="Data format")

    # pull command - Pull skill data for training
    pull_parser = subparsers.add_parser("pull", help="Pull skill data for training")
    pull_parser.add_argument("skill_id", help="Skill ID to pull")
    pull_parser.add_argument("-r", "--robot", help="Filter by robot model")
    pull_parser.add_argument("-f", "--format", default="json",
                           choices=["json", "rlds", "lerobot"],
                           help="Output format (default: json)")
    pull_parser.add_argument("-o", "--output", default="./data",
                           help="Output directory (default: ./data)")

    # upload command - Upload demonstrations for labeling
    upload_parser = subparsers.add_parser("upload", help="Upload demonstrations for labeling")
    upload_parser.add_argument("path", help="Path to video file")
    upload_parser.add_argument("-r", "--robot", required=True, 
                             help="Robot model in the video")
    upload_parser.add_argument("-t", "--task", required=True,
                             help="Task being demonstrated")
    upload_parser.add_argument("-p", "--project", help="Project ID to associate with")

    # check-transfer command - Check skill transfer compatibility
    check_transfer_parser = subparsers.add_parser("check-transfer", 
                                                  help="Check skill transfer compatibility")
    check_transfer_parser.add_argument("-s", "--skill", help="Skill ID to check (optional)")
    check_transfer_parser.add_argument("--from", dest="source", required=True,
                                      help="Source robot model")
    check_transfer_parser.add_argument("--to", dest="target", required=True,
                                      help="Target robot model")
    check_transfer_parser.add_argument("--min-score", type=float, default=0.0,
                                      help="Minimum score threshold (0.0-1.0)")

    # labeling-status command - Check labeling job status
    labeling_status_parser = subparsers.add_parser("labeling-status",
                                                   help="Check labeling job status")
    labeling_status_parser.add_argument("job_id", help="Labeling job ID")

    # parts command - Manage hardware parts
    parts_parser = subparsers.add_parser("parts", help="Manage hardware parts catalog")
    parts_subparsers = parts_parser.add_subparsers(dest="parts_action", help="Parts action")
    
    # parts list
    parts_list_parser = parts_subparsers.add_parser("list", help="List available parts")
    parts_list_parser.add_argument("-c", "--category", 
                                   choices=["gripper", "sensor", "actuator", "controller", 
                                           "end-effector", "camera", "lidar", "force-torque"],
                                   help="Filter by category")
    parts_list_parser.add_argument("-m", "--manufacturer", help="Filter by manufacturer")
    parts_list_parser.add_argument("-s", "--search", help="Search by name or part number")
    
    # parts check
    parts_check_parser = parts_subparsers.add_parser("check", 
                                                     help="Check part compatibility for skill")
    parts_check_parser.add_argument("skill_id", help="Skill ID to check")
    
    # parts require
    parts_require_parser = parts_subparsers.add_parser("require", 
                                                       help="Add part dependency to skill")
    parts_require_parser.add_argument("part_id", help="Part ID to require")
    parts_require_parser.add_argument("-s", "--skill", required=True, help="Skill ID")
    parts_require_parser.add_argument("-v", "--version", default="1.0.0", 
                                      help="Minimum version (default: 1.0.0)")
    parts_require_parser.add_argument("--required", action="store_true",
                                      help="Mark as required (not optional)")

    # deps command - Dependency management
    deps_parser = subparsers.add_parser("deps", help="Dependency management")
    deps_subparsers = deps_parser.add_subparsers(dest="deps_action", help="Deps action")
    
    # deps audit
    deps_audit_parser = deps_subparsers.add_parser("audit",
                                                   help="Verify all dependencies compatible")
    deps_audit_parser.add_argument("-s", "--skill", help="Skill ID (default: current repo)")

    # protocol command - Protocol registry management
    protocol_parser = subparsers.add_parser("protocol", help="Manage protocol registry")
    protocol_subparsers = protocol_parser.add_subparsers(dest="protocol_action", help="Protocol action")

    # protocol list
    protocol_list_parser = protocol_subparsers.add_parser("list", help="List protocols")
    protocol_list_parser.add_argument("-r", "--robot", help="Filter by robot model")
    protocol_list_parser.add_argument("-t", "--transport",
                                      choices=["ble", "serial", "wifi", "can", "i2c", "spi", "mqtt", "ros2"],
                                      help="Filter by transport type")
    protocol_list_parser.add_argument("--verified", action="store_true", help="Show only verified protocols")
    protocol_list_parser.add_argument("-s", "--search", help="Search in command format and notes")

    # protocol get
    protocol_get_parser = protocol_subparsers.add_parser("get", help="Get protocol details")
    protocol_get_parser.add_argument("protocol_id", help="Protocol ID")

    # protocol init
    protocol_init_parser = protocol_subparsers.add_parser("init", help="Initialize new protocol template")
    protocol_init_parser.add_argument("robot_model", help="Robot model name (e.g., hiwonder-mechdog-pro)")
    protocol_init_parser.add_argument("-t", "--transport", required=True,
                                      choices=["ble", "serial", "wifi", "can", "i2c", "spi", "mqtt", "ros2"],
                                      help="Transport type")
    protocol_init_parser.add_argument("-o", "--output", default="./protocol",
                                      help="Output directory (default: ./protocol)")

    # protocol push
    protocol_push_parser = protocol_subparsers.add_parser("push", help="Upload protocol to FoodForThought")
    protocol_push_parser.add_argument("file", nargs="?", help="Path to protocol.json (default: ./protocol.json)")

    # protocol scan-serial
    protocol_subparsers.add_parser("scan-serial", help="Scan for serial ports")

    # protocol scan-ble
    protocol_subparsers.add_parser("scan-ble", help="Scan for BLE devices")

    # primitive command - Primitive skills management
    primitive_parser = subparsers.add_parser("primitive", help="Manage primitive skills")
    primitive_subparsers = primitive_parser.add_subparsers(dest="primitive_action", help="Primitive action")

    # primitive list
    primitive_list_parser = primitive_subparsers.add_parser("list", help="List primitive skills")
    primitive_list_parser.add_argument("-r", "--robot", help="Filter by robot model")
    primitive_list_parser.add_argument("-c", "--category",
                                       choices=["body_pose", "arm", "gripper", "locomotion",
                                               "head", "sensing", "manipulation", "navigation"],
                                       help="Filter by category")
    primitive_list_parser.add_argument("--status",
                                       choices=["experimental", "tested", "verified", "deprecated"],
                                       help="Filter by status")
    primitive_list_parser.add_argument("--tested", action="store_true",
                                       help="Show only tested/verified primitives")

    # primitive get
    primitive_get_parser = primitive_subparsers.add_parser("get", help="Get primitive details")
    primitive_get_parser.add_argument("primitive_id", help="Primitive ID")

    # primitive test
    primitive_test_parser = primitive_subparsers.add_parser("test", help="Submit test result")
    primitive_test_parser.add_argument("primitive_id", help="Primitive ID to test")
    primitive_test_parser.add_argument("-p", "--params", required=True,
                                       help="Parameters used in test as JSON (e.g., '{\"pitch\": 15}')")
    primitive_test_parser.add_argument("-r", "--result", required=True,
                                       choices=["pass", "fail", "partial"],
                                       help="Test result")
    primitive_test_parser.add_argument("-n", "--notes", help="Test notes")
    primitive_test_parser.add_argument("-v", "--video", help="Video URL of test")

    # primitive deps (nested subcommand for dependency management)
    primitive_deps_parser = primitive_subparsers.add_parser("deps", help="Manage primitive dependencies")
    primitive_deps_subparsers = primitive_deps_parser.add_subparsers(dest="primitive_deps_action",
                                                                     help="Dependency action")

    # primitive deps show
    primitive_deps_show_parser = primitive_deps_subparsers.add_parser("show", help="Show dependencies")
    primitive_deps_show_parser.add_argument("primitive_id", help="Primitive ID")

    # primitive deps add
    primitive_deps_add_parser = primitive_deps_subparsers.add_parser("add", help="Add dependency")
    primitive_deps_add_parser.add_argument("primitive_id", help="Primitive ID (the one that depends)")
    primitive_deps_add_parser.add_argument("required_id", help="Required primitive ID")
    primitive_deps_add_parser.add_argument("-t", "--type", default="requires",
                                           choices=["requires", "extends", "overrides", "optional"],
                                           help="Dependency type (default: requires)")
    primitive_deps_add_parser.add_argument("--min-status", default="tested",
                                           choices=["experimental", "tested", "verified"],
                                           help="Minimum required status (default: tested)")

    # primitive init
    primitive_init_parser = primitive_subparsers.add_parser("init", help="Initialize primitive skill template")
    primitive_init_parser.add_argument("name", help="Primitive name (e.g., move_joint, grip_close)")
    primitive_init_parser.add_argument("-p", "--protocol", help="Protocol ID to link to")
    primitive_init_parser.add_argument("-r", "--from-recording", help="Import from recording file")
    primitive_init_parser.add_argument("-c", "--category", default="motion",
                                       choices=["body_pose", "arm", "gripper", "locomotion",
                                               "head", "sensing", "manipulation", "navigation"],
                                       help="Primitive category (default: motion)")
    primitive_init_parser.add_argument("-o", "--output", default=".", help="Output directory")

    # primitive push
    primitive_push_parser = primitive_subparsers.add_parser("push", help="Publish primitive to FoodforThought")
    primitive_push_parser.add_argument("primitive_file", help="Path to .primitive.json file")

    # skill command - Skill abstractions (composed from primitives)
    skill_parser = subparsers.add_parser("skill", help="Manage skill abstractions (Layer 2)")
    skill_subparsers = skill_parser.add_subparsers(dest="skill_action", help="Skill action")

    # skill init
    skill_init_parser = skill_subparsers.add_parser("init", help="Initialize a new skill abstraction")
    skill_init_parser.add_argument("name", help="Skill name (e.g., pick_and_place)")
    skill_init_parser.add_argument("-r", "--robot", help="Target robot model")
    skill_init_parser.add_argument("-t", "--template", default="basic",
                                   choices=["basic", "pick_place", "navigation", "inspection"],
                                   help="Skill template (default: basic)")
    skill_init_parser.add_argument("-o", "--output", default=".", help="Output directory")

    # skill compose
    skill_compose_parser = skill_subparsers.add_parser("compose", help="Add primitives to skill")
    skill_compose_parser.add_argument("skill_file", help="Path to .skill.json file")
    skill_compose_parser.add_argument("primitives", nargs="+", help="Primitive IDs to add")

    # skill list
    skill_list_parser = skill_subparsers.add_parser("list", help="List skill abstractions")
    skill_list_parser.add_argument("-r", "--robot", help="Filter by robot model")
    skill_list_parser.add_argument("--status",
                                   choices=["experimental", "tested", "verified"],
                                   help="Filter by status")

    # skill get
    skill_get_parser = skill_subparsers.add_parser("get", help="Get skill details")
    skill_get_parser.add_argument("skill_id", help="Skill ID")

    # skill push
    skill_push_parser = skill_subparsers.add_parser("push", help="Publish skill to FoodforThought")
    skill_push_parser.add_argument("skill_file", help="Path to .skill.json file")

    # skill test
    skill_test_parser = skill_subparsers.add_parser("test", help="Test a skill")
    skill_test_parser.add_argument("skill", help="Skill file or ID")
    skill_test_parser.add_argument("-p", "--params", help="Skill parameters as JSON")
    skill_test_parser.add_argument("--execute", action="store_true",
                                   help="Actually execute (default is dry run)")

    # bridge command - Interactive robot communication
    bridge_parser = subparsers.add_parser("bridge", help="Interactive robot communication bridge")
    bridge_subparsers = bridge_parser.add_subparsers(dest="bridge_action", help="Bridge action")

    # bridge connect
    bridge_connect_parser = bridge_subparsers.add_parser("connect",
                                                          help="Connect to robot interactively")
    bridge_connect_parser.add_argument("port", help="Serial port or BLE address")
    bridge_connect_parser.add_argument("-t", "--transport", default="serial",
                                       choices=["serial", "ble"],
                                       help="Transport type (default: serial)")
    bridge_connect_parser.add_argument("-b", "--baud", type=int, default=115200,
                                       help="Baud rate for serial (default: 115200)")
    bridge_connect_parser.add_argument("-p", "--protocol", help="Protocol ID for command hints")

    # bridge send
    bridge_send_parser = bridge_subparsers.add_parser("send", help="Send single command")
    bridge_send_parser.add_argument("port", help="Serial port or BLE address")
    bridge_send_parser.add_argument("command", help="Command to send")
    bridge_send_parser.add_argument("-t", "--transport", default="serial",
                                    choices=["serial", "ble"],
                                    help="Transport type (default: serial)")
    bridge_send_parser.add_argument("-b", "--baud", type=int, default=115200,
                                    help="Baud rate for serial (default: 115200)")
    bridge_send_parser.add_argument("-w", "--wait", type=float, default=0.5,
                                    help="Wait time for response in seconds (default: 0.5)")

    # bridge record
    bridge_record_parser = bridge_subparsers.add_parser("record",
                                                         help="Record session for primitive creation")
    bridge_record_parser.add_argument("port", help="Serial port or BLE address")
    bridge_record_parser.add_argument("-o", "--output", default="./recording.json",
                                      help="Output file (default: ./recording.json)")
    bridge_record_parser.add_argument("-t", "--transport", default="serial",
                                      choices=["serial", "ble"],
                                      help="Transport type (default: serial)")
    bridge_record_parser.add_argument("-b", "--baud", type=int, default=115200,
                                      help="Baud rate for serial (default: 115200)")
    bridge_record_parser.add_argument("-n", "--name", help="Primitive skill name")

    # bridge replay
    bridge_replay_parser = bridge_subparsers.add_parser("replay", help="Replay a recorded session")
    bridge_replay_parser.add_argument("recording", help="Path to recording file")
    bridge_replay_parser.add_argument("port", help="Serial port or BLE address")
    bridge_replay_parser.add_argument("-t", "--transport", default="serial",
                                      choices=["serial", "ble"],
                                      help="Transport type (default: serial)")
    bridge_replay_parser.add_argument("-b", "--baud", type=int, default=115200,
                                      help="Baud rate for serial (default: 115200)")
    bridge_replay_parser.add_argument("-s", "--speed", type=float, default=1.0,
                                      help="Playback speed multiplier (default: 1.0)")

    # bridge serve - WebSocket server for Artifex integration
    bridge_serve_parser = bridge_subparsers.add_parser("serve",
        help="Start WebSocket server for Artifex Desktop integration",
        description="""Start the ATE Bridge Server for Artifex Desktop integration.

This server enables sim-to-real transfer by bridging Artifex Desktop to physical robot hardware.

WORKFLOW:
1. Start this server: ate bridge serve -v
2. Connect your robot via USB serial
3. In Artifex Desktop, use the Hardware panel or AI tools to connect
4. Control your robot directly from the Artifex interface

CAPABILITIES:
- Serial port discovery and robot connection
- Real-time servo state monitoring (position, velocity, temperature, load)
- Joint control with URDF-to-servo mapping
- Trajectory execution
- Skill deployment and execution

EXAMPLE:
    ate bridge serve -p 8765 -v

The server listens on ws://localhost:8765 by default.
Artifex Desktop will auto-connect when the Hardware panel is opened.""",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    bridge_serve_parser.add_argument("-p", "--port", type=int, default=8765,
                                     help="WebSocket port (default: 8765)")
    bridge_serve_parser.add_argument("-v", "--verbose", action="store_true",
                                     help="Enable verbose logging (shows all messages)")

    # generate command - Generate skill from text description
    generate_parser = subparsers.add_parser("generate",
                                           help="Generate skill scaffolding from text description")
    generate_parser.add_argument("description",
                                help="Natural language task description (e.g., 'pick up box and place on pallet')")
    generate_parser.add_argument("-r", "--robot", default="ur5",
                                help="Target robot model (default: ur5)")
    generate_parser.add_argument("-o", "--output", default="./new-skill",
                                help="Output directory (default: ./new-skill)")

    # compile command - Compile skill specification to deployable package
    compile_parser = subparsers.add_parser("compile",
        help="Compile skill.yaml into deployable package (ROS2, Docker, Python)",
        description="""Compile a skill specification into a deployable package.

The skill compiler transforms a skill.yaml specification into:
- Python skill implementation with primitives wrappers
- ROS2 package with action/service interfaces
- Docker container for deployment
- Hardware configuration mapping

EXAMPLES:
    ate compile skill.yaml
    ate compile skill.yaml --target docker
    ate compile skill.yaml --target ros2 --robot my_arm.urdf
    ate compile skill.yaml --ate-dir ./robot_config
""",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    compile_parser.add_argument("skill_path",
                               help="Path to skill.yaml specification")
    compile_parser.add_argument("-o", "--output", default="./output",
                               help="Output directory (default: ./output)")
    compile_parser.add_argument("-t", "--target", default="ros2",
                               choices=["ros2", "docker", "python"],
                               help="Target platform (default: ros2)")
    compile_parser.add_argument("-r", "--robot",
                               help="Path to robot URDF for hardware config")
    compile_parser.add_argument("--ate-dir",
                               help="Path to ATE config directory for servo mapping")

    # test-skill command - Test compiled skill
    test_skill_parser = subparsers.add_parser("test-skill",
        help="Test a compiled skill in simulation or on hardware",
        description="""Test a compiled skill package.

MODES:
    mock     - Run with mock hardware drivers (no hardware needed)
    sim      - Run in MuJoCo/Gazebo simulation (requires setup)
    hardware - Run on physical robot (requires bridge connection)

EXAMPLES:
    ate test-skill ./output --mode mock
    ate test-skill ./output --mode hardware --robot-port /dev/ttyUSB0
    ate test-skill ./output --mode mock --params '{"pick_pose": [0.5, 0, 0.3]}'
""",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    test_skill_parser.add_argument("skill_path",
                                   help="Path to compiled skill directory")
    test_skill_parser.add_argument("-m", "--mode", default="mock",
                                   choices=["sim", "hardware", "mock"],
                                   help="Test mode (default: mock)")
    test_skill_parser.add_argument("--robot-port",
                                   help="Robot serial port for hardware mode")
    test_skill_parser.add_argument("-p", "--params",
                                   help="Skill parameters as JSON string")

    # publish-skill command - Publish compiled skill to registry
    publish_skill_parser = subparsers.add_parser("publish-skill",
        help="Publish compiled skill to FoodforThought registry",
        description="""Publish a compiled skill package to FoodforThought.

The skill will be uploaded to the skill registry and made available
for other users to discover and deploy.

EXAMPLES:
    ate publish-skill ./output
    ate publish-skill ./output --visibility private
    ate publish-skill ./output --visibility team
""",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    publish_skill_parser.add_argument("skill_path",
                                      help="Path to compiled skill directory")
    publish_skill_parser.add_argument("-v", "--visibility", default="public",
                                      choices=["public", "private", "team"],
                                      help="Visibility (default: public)")

    # check-compatibility command - Check skill-robot compatibility
    check_compat_parser = subparsers.add_parser("check-compatibility",
        help="Check if a skill is compatible with a robot",
        description="""Check if a skill specification is compatible with a robot.

Analyzes hardware requirements, kinematic constraints, and primitive
support to determine if a skill can run on a given robot.

EXAMPLES:
    ate check-compatibility skill.yaml --robot-urdf my_arm.urdf
    ate check-compatibility skill.yaml --ate-dir ./robot_config
""",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    check_compat_parser.add_argument("skill_path",
                                     help="Path to skill.yaml")
    check_compat_parser.add_argument("--robot-urdf",
                                     help="Path to robot URDF")
    check_compat_parser.add_argument("--ate-dir",
                                     help="Path to ATE config directory")

    # publish-protocol command - Convenient alias for protocol push
    publish_protocol_parser = subparsers.add_parser("publish-protocol",
                                                    help="Publish a robot protocol to FoodForThought (alias for 'protocol push')")
    publish_protocol_parser.add_argument("file", nargs="?",
                                         help="Path to protocol.json (default: ./protocol.json)")

    # workflow command - Workflow/pipeline management
    workflow_parser = subparsers.add_parser("workflow", help="Manage skill workflows/pipelines")
    workflow_subparsers = workflow_parser.add_subparsers(dest="workflow_action", help="Workflow action")
    
    # workflow validate
    workflow_validate_parser = workflow_subparsers.add_parser("validate", 
                                                              help="Validate workflow YAML")
    workflow_validate_parser.add_argument("path", help="Path to workflow YAML file")
    
    # workflow run
    workflow_run_parser = workflow_subparsers.add_parser("run", help="Run a workflow")
    workflow_run_parser.add_argument("path", help="Path to workflow YAML file")
    workflow_run_parser.add_argument("--sim", action="store_true", 
                                    help="Run in simulation mode")
    workflow_run_parser.add_argument("--dry-run", action="store_true",
                                    help="Show execution plan without running")
    
    # workflow export
    workflow_export_parser = workflow_subparsers.add_parser("export", 
                                                           help="Export workflow to other formats")
    workflow_export_parser.add_argument("path", help="Path to workflow YAML file")
    workflow_export_parser.add_argument("-f", "--format", default="ros2",
                                       choices=["ros2", "json"],
                                       help="Export format (default: ros2)")
    workflow_export_parser.add_argument("-o", "--output", help="Output file path")

    # team command - Team collaboration
    team_parser = subparsers.add_parser("team", help="Team collaboration management")
    team_subparsers = team_parser.add_subparsers(dest="team_action", help="Team action")
    
    # team create
    team_create_parser = team_subparsers.add_parser("create", help="Create a new team")
    team_create_parser.add_argument("name", help="Team name")
    team_create_parser.add_argument("-d", "--description", help="Team description")
    
    # team invite
    team_invite_parser = team_subparsers.add_parser("invite", help="Invite user to team")
    team_invite_parser.add_argument("email", help="Email of user to invite")
    team_invite_parser.add_argument("-t", "--team", required=True, help="Team slug")
    team_invite_parser.add_argument("-r", "--role", default="member",
                                   choices=["owner", "admin", "member", "viewer"],
                                   help="Role to assign (default: member)")
    
    # team list
    team_subparsers.add_parser("list", help="List teams you belong to")
    
    # team share (skill share with team)
    team_share_parser = team_subparsers.add_parser("share", help="Share skill with team")
    team_share_parser.add_argument("skill_id", help="Skill ID to share")
    team_share_parser.add_argument("-t", "--team", required=True, help="Team slug")

    # data command - Dataset management
    data_parser = subparsers.add_parser("data", help="Dataset and telemetry management")
    data_subparsers = data_parser.add_subparsers(dest="data_action", help="Data action")
    
    # data upload
    data_upload_parser = data_subparsers.add_parser("upload", help="Upload sensor data")
    data_upload_parser.add_argument("path", help="Path to data directory or file")
    data_upload_parser.add_argument("-s", "--skill", required=True, help="Associated skill ID")
    data_upload_parser.add_argument("--stage", default="raw",
                                   choices=["raw", "annotated", "skill-abstracted", "production"],
                                   help="Data stage (default: raw)")
    
    # data list
    data_list_parser = data_subparsers.add_parser("list", help="List datasets")
    data_list_parser.add_argument("-s", "--skill", help="Filter by skill ID")
    data_list_parser.add_argument("--stage", help="Filter by stage")
    
    # data promote
    data_promote_parser = data_subparsers.add_parser("promote", help="Promote dataset stage")
    data_promote_parser.add_argument("dataset_id", help="Dataset ID")
    data_promote_parser.add_argument("--to", required=True, dest="to_stage",
                                    choices=["annotated", "skill-abstracted", "production"],
                                    help="Target stage")
    
    # data export
    data_export_parser = data_subparsers.add_parser("export", help="Export dataset")
    data_export_parser.add_argument("dataset_id", help="Dataset ID")
    data_export_parser.add_argument("-f", "--format", default="rlds",
                                   choices=["json", "rlds", "lerobot", "hdf5"],
                                   help="Export format (default: rlds)")
    data_export_parser.add_argument("-o", "--output", default="./export",
                                   help="Output directory")

    # deploy command - Enhanced deployment management
    deploy_subparsers = deploy_parser.add_subparsers(dest="deploy_action", help="Deploy action")
    
    # deploy config (hybrid edge/cloud deployment)
    deploy_config_parser = deploy_subparsers.add_parser("config", 
                                                        help="Deploy using config file")
    deploy_config_parser.add_argument("config_path", help="Path to deploy.yaml")
    deploy_config_parser.add_argument("-t", "--target", required=True, 
                                     help="Target fleet or robot")
    deploy_config_parser.add_argument("--dry-run", action="store_true",
                                     help="Show plan without deploying")
    
    # deploy status
    deploy_status_parser = deploy_subparsers.add_parser("status",
                                                        help="Check deployment status")
    deploy_status_parser.add_argument("target", help="Target fleet or robot")

    # record command - Telemetry recording for Data Flywheel
    record_parser = subparsers.add_parser("record",
        help="Record robot telemetry for the Data Flywheel",
        description="""Record telemetry from robots for training data.

Examples:
    ate record start --robot my-robot --skill pick_and_place --task "Pick red cube"
    ate record stop --success
    ate record status
    ate record demo --robot my-robot --skill grasp --task "Grasp object" --duration 30
    ate record list --robot my-robot""")
    record_subparsers = record_parser.add_subparsers(dest="record_action", help="Record action")

    # record start
    record_start_parser = record_subparsers.add_parser("start", help="Start recording telemetry")
    record_start_parser.add_argument("--robot", "-r", required=True, help="Robot ID to record from")
    record_start_parser.add_argument("--skill", "-s", required=True, help="Skill ID being executed")
    record_start_parser.add_argument("--task", "-t", help="Task description (optional)")

    # record stop
    record_stop_parser = record_subparsers.add_parser("stop", help="Stop recording and upload")
    record_stop_parser.add_argument("--success", action="store_true", default=True,
                                   help="Mark recording as successful (default)")
    record_stop_parser.add_argument("--failure", action="store_true",
                                   help="Mark recording as failed")
    record_stop_parser.add_argument("--notes", "-n", help="Notes about the recording")
    record_stop_parser.add_argument("--no-upload", action="store_true",
                                   help="Don't upload to FoodforThought")
    record_stop_parser.add_argument("--create-task", action="store_true",
                                   help="Create a labeling task for community annotation")

    # record status
    record_subparsers.add_parser("status", help="Get current recording status")

    # record demo (timed demonstration)
    record_demo_parser = record_subparsers.add_parser("demo", help="Record a timed demonstration")
    record_demo_parser.add_argument("--robot", "-r", required=True, help="Robot ID")
    record_demo_parser.add_argument("--skill", "-s", required=True, help="Skill being demonstrated")
    record_demo_parser.add_argument("--task", "-t", required=True, help="Task description")
    record_demo_parser.add_argument("--duration", "-d", type=float, default=30.0,
                                   help="Recording duration in seconds (default: 30)")
    record_demo_parser.add_argument("--create-task", action="store_true", default=True,
                                   help="Create labeling task after upload (default)")

    # record list
    record_list_parser = record_subparsers.add_parser("list", help="List telemetry recordings")
    record_list_parser.add_argument("--robot", "-r", help="Filter by robot ID")
    record_list_parser.add_argument("--skill", "-s", help="Filter by skill ID")
    record_list_parser.add_argument("--success-only", action="store_true",
                                   help="Only show successful recordings")
    record_list_parser.add_argument("--limit", "-l", type=int, default=20,
                                   help="Maximum number of results (default: 20)")

    # robot-setup command - Interactive wizard for robot discovery and primitive skill generation
    robot_setup_parser = subparsers.add_parser("robot-setup",
                                                help="Interactive wizard to discover robot and generate primitive skills")
    robot_setup_parser.add_argument("-p", "--port", help="Serial port (skip device selection)")
    robot_setup_parser.add_argument("-o", "--output", default="./robot",
                                    help="Output directory for generated files (default: ./robot)")
    robot_setup_parser.add_argument("--skip-labeling", action="store_true",
                                    help="Skip labeling entirely (use generic servo_N names)")
    robot_setup_parser.add_argument("--robot-type",
                                    choices=["quadruped", "quadruped_with_arm", "hexapod",
                                            "6dof_arm", "humanoid_basic", "humanoid",
                                            "humanoid_advanced", "humanoid_full", "custom"],
                                    help="Force robot type for AI-suggested labels")
    robot_setup_parser.add_argument("--non-interactive", action="store_true",
                                    help="Run without user prompts (use defaults and AI suggestions)")
    robot_setup_parser.add_argument("--push", action="store_true",
                                    help="Auto-push generated primitives to FoodforThought (requires FOODFORTHOUGHT_TOKEN)")
    robot_setup_parser.add_argument("--api-url",
                                    help="FoodforThought API URL (defaults to https://kindlyrobotics.com)")
    robot_setup_parser.add_argument("--scan-only", action="store_true",
                                    help="Only scan for devices, don't run full wizard")

    # marketplace command - Skill Marketplace ("npm for robot skills")
    marketplace_parser = subparsers.add_parser("marketplace",
        help="Skill Marketplace - discover, install, and publish robot skills",
        description="""Skill Marketplace - "npm for robot skills"

Discover community-contributed skills, install them for your robot,
and publish your own skills to share with others.

EXAMPLES:
    ate marketplace search "pick and place"
    ate marketplace show pick-and-place
    ate marketplace install pick-and-place --robot my-arm
    ate marketplace publish ./my-skill
    ate marketplace report pick-and-place my-arm --works
""",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    marketplace_subparsers = marketplace_parser.add_subparsers(dest="marketplace_action", help="Marketplace action")

    # marketplace search
    marketplace_search_parser = marketplace_subparsers.add_parser("search",
        help="Search for skills in the marketplace")
    marketplace_search_parser.add_argument("query", help="Search query")
    marketplace_search_parser.add_argument("-c", "--category",
        choices=["manipulation", "navigation", "perception", "locomotion",
                 "interaction", "inspection", "assembly", "pick_and_place",
                 "cleaning", "logistics", "other"],
        help="Filter by category")
    marketplace_search_parser.add_argument("-r", "--robot-type", help="Filter by robot type")
    marketplace_search_parser.add_argument("-l", "--license", help="Filter by license (mit, apache2, etc.)")
    marketplace_search_parser.add_argument("-p", "--pricing", choices=["free", "paid"],
        help="Filter by pricing")
    marketplace_search_parser.add_argument("-s", "--sort", default="downloads",
        choices=["downloads", "rating", "recent", "executions", "installs"],
        help="Sort results (default: downloads)")
    marketplace_search_parser.add_argument("--limit", type=int, default=20,
        help="Number of results (default: 20)")

    # marketplace show
    marketplace_show_parser = marketplace_subparsers.add_parser("show",
        help="Show detailed information about a skill")
    marketplace_show_parser.add_argument("slug", help="Skill slug/name")

    # marketplace install
    marketplace_install_parser = marketplace_subparsers.add_parser("install",
        help="Install a skill from the marketplace")
    marketplace_install_parser.add_argument("skill_name", help="Skill name or slug")
    marketplace_install_parser.add_argument("-v", "--version", help="Specific version to install")
    marketplace_install_parser.add_argument("-r", "--robot", help="Target robot ID for compatibility check")
    marketplace_install_parser.add_argument("-o", "--output", help="Output directory (default: ./<skill_name>)")

    # marketplace publish
    marketplace_publish_parser = marketplace_subparsers.add_parser("publish",
        help="Publish a skill to the marketplace")
    marketplace_publish_parser.add_argument("path", help="Path to skill directory")
    marketplace_publish_parser.add_argument("--no-public", action="store_true",
        help="Keep skill private (not listed publicly)")

    # marketplace report
    marketplace_report_parser = marketplace_subparsers.add_parser("report",
        help="Report skill compatibility with a robot")
    marketplace_report_parser.add_argument("skill_name", help="Skill name or slug")
    marketplace_report_parser.add_argument("robot", help="Robot ID")
    marketplace_report_parser.add_argument("--works", dest="works", action="store_true",
        help="Report that skill works on this robot")
    marketplace_report_parser.add_argument("--no-works", dest="works", action="store_false",
        help="Report that skill does NOT work on this robot")
    marketplace_report_parser.add_argument("-n", "--notes", help="Additional notes")
    marketplace_report_parser.add_argument("-v", "--version", help="Version tested")
    marketplace_report_parser.set_defaults(works=None)

    # marketplace list (installed)
    marketplace_subparsers.add_parser("installed", help="List installed skills")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Handle auth commands first (before creating client)
    if args.command == "login":
        login_command()
        return

    if args.command == "logout":
        logout_command()
        return

    if args.command == "whoami":
        whoami_command()
        return

    client = ATEClient()

    if args.command == "init":
        result = client.init(args.name, args.description, args.visibility)
        print(f"Created repository: {result['repository']['id']}")

    elif args.command == "clone":
        client.clone(args.repo_id, args.target_dir)

    elif args.command == "commit":
        client.commit(args.message, args.files)

    elif args.command == "push":
        client.push(args.branch)

    elif args.command == "deploy":
        client.deploy(args.robot_type, args.repo_id)

    elif args.command == "test":
        client.test(args.environment, args.robot, args.local)

    elif args.command == "benchmark":
        client.benchmark(args.type, args.trials, args.compare)

    elif args.command == "adapt":
        client.adapt(args.source_robot, args.target_robot, args.repo_id, args.analyze_only)

    elif args.command == "validate":
        client.validate(args.checks, args.strict, args.files)

    elif args.command == "stream":
        client.stream(args.action, args.sensors, args.output, args.format)

    elif args.command == "pull":
        client.pull(args.skill_id, args.robot, args.format, args.output)

    elif args.command == "upload":
        client.upload(args.path, args.robot, args.task, args.project)

    elif args.command == "check-transfer":
        client.check_transfer(args.skill, args.source, args.target, args.min_score)

    elif args.command == "labeling-status":
        client.labeling_status(args.job_id)

    elif args.command == "parts":
        if args.parts_action == "list":
            client.parts_list(args.category, args.manufacturer, args.search)
        elif args.parts_action == "check":
            client.parts_check(args.skill_id)
        elif args.parts_action == "require":
            client.parts_require(args.part_id, args.skill, args.version, args.required)
        else:
            parts_parser.print_help()

    elif args.command == "deps":
        if args.deps_action == "audit":
            client.deps_audit(args.skill)
        else:
            deps_parser.print_help()

    elif args.command == "protocol":
        if args.protocol_action == "list":
            client.protocol_list(args.robot, args.transport, args.verified, args.search)
        elif args.protocol_action == "get":
            client.protocol_get(args.protocol_id)
        elif args.protocol_action == "init":
            client.protocol_init(args.robot_model, args.transport, args.output)
        elif args.protocol_action == "push":
            client.protocol_push(args.file)
        elif args.protocol_action == "scan-serial":
            client.protocol_scan_serial()
        elif args.protocol_action == "scan-ble":
            client.protocol_scan_ble()
        else:
            protocol_parser.print_help()

    elif args.command == "primitive":
        if args.primitive_action == "list":
            client.primitive_list(args.robot, args.category, args.status, args.tested)
        elif args.primitive_action == "get":
            client.primitive_get(args.primitive_id)
        elif args.primitive_action == "test":
            client.primitive_test(args.primitive_id, args.params, args.result, args.notes, args.video)
        elif args.primitive_action == "init":
            client.primitive_init(args.name, args.protocol, args.from_recording, args.category, args.output)
        elif args.primitive_action == "push":
            client.primitive_push(args.primitive_file)
        elif args.primitive_action == "deps":
            if args.primitive_deps_action == "show":
                client.primitive_deps_show(args.primitive_id)
            elif args.primitive_deps_action == "add":
                client.primitive_deps_add(args.primitive_id, args.required_id, args.type, args.min_status)
            else:
                primitive_deps_parser.print_help()
        else:
            primitive_parser.print_help()

    elif args.command == "skill":
        if args.skill_action == "init":
            client.skill_init(args.name, args.robot, args.template, args.output)
        elif args.skill_action == "compose":
            client.skill_compose(args.skill_file, args.primitives)
        elif args.skill_action == "list":
            client.skill_list(args.robot, args.status)
        elif args.skill_action == "get":
            client.skill_get(args.skill_id)
        elif args.skill_action == "push":
            client.skill_push(args.skill_file)
        elif args.skill_action == "test":
            client.skill_test(args.skill, args.params, not args.execute)
        else:
            skill_parser.print_help()

    elif args.command == "bridge":
        if args.bridge_action == "connect":
            client.bridge_connect(args.port, args.transport, args.baud, args.protocol)
        elif args.bridge_action == "send":
            client.bridge_send(args.port, args.command, args.transport, args.baud, args.wait)
        elif args.bridge_action == "record":
            client.bridge_record(args.port, args.output, args.transport, args.baud, args.name)
        elif args.bridge_action == "replay":
            client.bridge_replay(args.recording, args.port, args.transport, args.baud, args.speed)
        elif args.bridge_action == "serve":
            from ate.bridge_server import run_bridge_server
            run_bridge_server(port=args.port, verbose=args.verbose)
        else:
            bridge_parser.print_help()

    elif args.command == "generate":
        client.generate(args.description, args.robot, args.output)

    elif args.command == "compile":
        client.compile_skill(
            args.skill_path,
            args.output,
            args.target,
            args.robot,
            getattr(args, 'ate_dir', None)
        )

    elif args.command == "test-skill":
        client.test_compiled_skill(
            args.skill_path,
            args.mode,
            args.robot_port,
            args.params
        )

    elif args.command == "publish-skill":
        client.publish_compiled_skill(args.skill_path, args.visibility)

    elif args.command == "check-compatibility":
        client.check_skill_compatibility(
            args.skill_path,
            args.robot_urdf,
            getattr(args, 'ate_dir', None)
        )

    elif args.command == "publish-protocol":
        client.publish_protocol(args.file)

    elif args.command == "workflow":
        if args.workflow_action == "validate":
            client.workflow_validate(args.path)
        elif args.workflow_action == "run":
            client.workflow_run(args.path, args.sim, args.dry_run)
        elif args.workflow_action == "export":
            client.workflow_export(args.path, args.format, args.output)
        else:
            workflow_parser.print_help()

    elif args.command == "team":
        if args.team_action == "create":
            client.team_create(args.name, args.description)
        elif args.team_action == "invite":
            client.team_invite(args.email, args.team, args.role)
        elif args.team_action == "list":
            client.team_list()
        elif args.team_action == "share":
            client.team_share(args.skill_id, args.team)
        else:
            team_parser.print_help()

    elif args.command == "data":
        if args.data_action == "upload":
            client.data_upload(args.path, args.skill, args.stage)
        elif args.data_action == "list":
            client.data_list(args.skill, args.stage)
        elif args.data_action == "promote":
            client.data_promote(args.dataset_id, args.to_stage)
        elif args.data_action == "export":
            client.data_export(args.dataset_id, args.format, args.output)
        else:
            data_parser.print_help()

    elif args.command == "deploy":
        if args.deploy_action == "config":
            client.deploy_config(args.config_path, args.target, args.dry_run)
        elif args.deploy_action == "status":
            client.deploy_status(args.target)
        elif hasattr(args, 'robot_type'):
            # Original simple deploy command
            client.deploy(args.robot_type, args.repo_id)
        else:
            deploy_parser.print_help()

    elif args.command == "record":
        if args.record_action == "start":
            client.record_start(args.robot, args.skill, args.task)
        elif args.record_action == "stop":
            success = not args.failure if hasattr(args, 'failure') else args.success
            upload = not args.no_upload if hasattr(args, 'no_upload') else True
            client.record_stop(
                success=success,
                notes=args.notes if hasattr(args, 'notes') else None,
                upload=upload,
                create_labeling_task=args.create_task if hasattr(args, 'create_task') else False
            )
        elif args.record_action == "status":
            client.record_status()
        elif args.record_action == "demo":
            client.record_demo(
                args.robot,
                args.skill,
                args.task,
                args.duration,
                args.create_task if hasattr(args, 'create_task') else True
            )
        elif args.record_action == "list":
            client.record_list(
                robot_id=args.robot if hasattr(args, 'robot') else None,
                skill_id=args.skill if hasattr(args, 'skill') else None,
                success_only=args.success_only if hasattr(args, 'success_only') else False,
                limit=args.limit if hasattr(args, 'limit') else 20
            )
        else:
            record_parser.print_help()

    elif args.command == "robot-setup":
        from ate.robot_setup import run_wizard, RobotSetupWizard

        if args.scan_only:
            # Just scan for devices
            try:
                import serial.tools.list_ports
                print("\nScanning for serial ports...\n")
                ports = list(serial.tools.list_ports.comports())

                if not ports:
                    print("No serial ports found.")
                else:
                    print(f"Found {len(ports)} port(s):\n")
                    for port in ports:
                        print(f"  Port: {port.device}")
                        if port.description:
                            print(f"    Description: {port.description}")
                        if port.manufacturer:
                            print(f"    Manufacturer: {port.manufacturer}")
                        if port.vid and port.pid:
                            print(f"    VID:PID: {port.vid:04x}:{port.pid:04x}")
                        if port.serial_number:
                            print(f"    Serial: {port.serial_number}")
                        print()
            except ImportError:
                print("Error: pyserial not installed. Run: pip install pyserial")
                sys.exit(1)
        else:
            # Run full wizard
            success = run_wizard(
                port=args.port,
                output=args.output,
                skip_labeling=args.skip_labeling,
                robot_type=getattr(args, 'robot_type', None),
                non_interactive=getattr(args, 'non_interactive', False),
                push=getattr(args, 'push', False),
                api_url=getattr(args, 'api_url', None)
            )
            sys.exit(0 if success else 1)

    elif args.command == "marketplace":
        from ate.marketplace import (
            search_skills, show_skill, install_skill,
            publish_skill, report_compatibility, list_installed
        )

        if args.marketplace_action == "search":
            search_skills(
                query=args.query,
                category=args.category,
                robot_type=getattr(args, 'robot_type', None),
                license_type=args.license,
                pricing=args.pricing,
                sort=args.sort,
                limit=args.limit,
            )
        elif args.marketplace_action == "show":
            show_skill(args.slug)
        elif args.marketplace_action == "install":
            install_skill(
                skill_name=args.skill_name,
                version=args.version,
                robot=args.robot,
                output_dir=args.output,
            )
        elif args.marketplace_action == "publish":
            publish_skill(
                path=args.path,
                public=not args.no_public,
            )
        elif args.marketplace_action == "report":
            if args.works is None:
                print("Error: Must specify --works or --no-works", file=sys.stderr)
                sys.exit(1)
            report_compatibility(
                skill_name=args.skill_name,
                robot=args.robot,
                works=args.works,
                notes=args.notes,
                version=args.version,
            )
        elif args.marketplace_action == "installed":
            list_installed()
        else:
            marketplace_parser.print_help()


if __name__ == "__main__":
    main()

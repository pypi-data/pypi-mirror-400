"""
Telemetry CLI Commands

Provides command-line interface for telemetry operations:
- Status checking
- Recording management
- Upload/download
- Fleet agent control
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional

from .collector import TelemetryCollector
from .types import TrajectoryRecording, TelemetrySource
from .fleet_agent import FleetTelemetryAgent, run_fleet_agent


def add_telemetry_subparsers(subparsers) -> None:
    """
    Add telemetry subparsers to the main CLI parser.

    Usage in main cli.py:
        from ate.telemetry.cli import add_telemetry_subparsers
        add_telemetry_subparsers(subparsers)
    """
    telemetry_parser = subparsers.add_parser(
        "telemetry",
        help="Telemetry data management",
        description="""Manage telemetry data collection, upload, and analysis.

EXAMPLES:
    ate telemetry status
    ate telemetry upload recording.json
    ate telemetry list --robot my-robot
    ate telemetry agent my-robot --daemon
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    telemetry_subparsers = telemetry_parser.add_subparsers(
        dest="telemetry_action", help="Telemetry action"
    )

    # telemetry status
    telemetry_subparsers.add_parser(
        "status",
        help="Show telemetry collection status and configuration",
    )

    # telemetry upload
    upload_parser = telemetry_subparsers.add_parser(
        "upload",
        help="Upload a telemetry file to FoodforThought",
    )
    upload_parser.add_argument("file", help="Path to telemetry file (JSON, MCAP, or HDF5)")
    upload_parser.add_argument(
        "-f", "--format", default="auto",
        choices=["auto", "json", "mcap", "hdf5"],
        help="File format (default: auto-detect)",
    )
    upload_parser.add_argument("--robot-id", help="Override robot ID in recording")
    upload_parser.add_argument("--skill-id", help="Associate with skill ID")
    upload_parser.add_argument("--project-id", help="FoodforThought project ID")
    upload_parser.add_argument(
        "--tags", help="Comma-separated tags to add"
    )

    # telemetry export
    export_parser = telemetry_subparsers.add_parser(
        "export",
        help="Download and export telemetry from FoodforThought",
    )
    export_parser.add_argument("artifact_id", help="Artifact ID to download")
    export_parser.add_argument(
        "-o", "--output", default=".",
        help="Output directory (default: current directory)",
    )
    export_parser.add_argument(
        "-f", "--format", default="mcap",
        choices=["json", "mcap", "hdf5", "csv"],
        help="Export format (default: mcap)",
    )

    # telemetry list
    list_parser = telemetry_subparsers.add_parser(
        "list",
        help="List telemetry recordings from FoodforThought",
    )
    list_parser.add_argument("--robot-id", help="Filter by robot ID")
    list_parser.add_argument("--skill-id", help="Filter by skill ID")
    list_parser.add_argument(
        "--source", choices=["simulation", "hardware", "fleet"],
        help="Filter by source",
    )
    list_parser.add_argument("--success", type=bool, help="Filter by success status")
    list_parser.add_argument("--limit", type=int, default=20, help="Max results")
    list_parser.add_argument(
        "--format", choices=["table", "json"], default="table",
        help="Output format",
    )

    # telemetry agent
    agent_parser = telemetry_subparsers.add_parser(
        "agent",
        help="Start the fleet telemetry agent",
        description="""Start a background agent for continuous telemetry collection.

The agent runs on each fleet robot, collecting state data at a configurable
frequency and periodically uploading to FoodforThought.

EXAMPLES:
    ate telemetry agent my-robot-001
    ate telemetry agent my-robot-001 --daemon
    ate telemetry agent my-robot-001 --collection-hz 100 --upload-interval 30
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    agent_parser.add_argument("robot_id", help="Unique robot identifier")
    agent_parser.add_argument(
        "--daemon", action="store_true",
        help="Run as daemon (detach from terminal)",
    )
    agent_parser.add_argument(
        "--collection-hz", type=float, default=50.0,
        help="Collection frequency in Hz (default: 50)",
    )
    agent_parser.add_argument(
        "--upload-interval", type=float, default=60.0,
        help="Upload interval in seconds (default: 60)",
    )
    agent_parser.add_argument("--api-key", help="FoodforThought API key")
    agent_parser.add_argument("--project-id", help="FoodforThought project ID")

    # telemetry record
    record_parser = telemetry_subparsers.add_parser(
        "record",
        help="Record telemetry from stdin (pipe from robot)",
        description="""Record telemetry data from stdin.

Useful for piping robot state data directly to a recording.

EXAMPLES:
    robot_state_stream | ate telemetry record my-robot --skill pick_and_place
    ate telemetry record my-robot < state_dump.jsonl
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    record_parser.add_argument("robot_id", help="Robot identifier")
    record_parser.add_argument("--skill-id", help="Associated skill ID")
    record_parser.add_argument(
        "-o", "--output", help="Save recording to file (default: upload to FFT)"
    )
    record_parser.add_argument(
        "-f", "--format", default="json",
        choices=["json", "mcap", "hdf5"],
        help="Output format (default: json)",
    )


def handle_telemetry_command(args, client) -> None:
    """Handle telemetry subcommands."""
    if args.telemetry_action == "status":
        _handle_status(args, client)
    elif args.telemetry_action == "upload":
        _handle_upload(args, client)
    elif args.telemetry_action == "export":
        _handle_export(args, client)
    elif args.telemetry_action == "list":
        _handle_list(args, client)
    elif args.telemetry_action == "agent":
        _handle_agent(args)
    elif args.telemetry_action == "record":
        _handle_record(args, client)
    else:
        print("Please specify a telemetry action. Use 'ate telemetry --help' for options.")
        sys.exit(1)


def _handle_status(args, client) -> None:
    """Show telemetry status and configuration."""
    api_key = os.getenv("FFT_API_KEY") or os.getenv("ATE_API_KEY")
    api_url = os.getenv("FFT_API_URL", "https://kindly.fyi/api")
    project_id = os.getenv("FFT_PROJECT_ID")

    print("\n=== Telemetry Configuration ===\n")
    print(f"API URL:      {api_url}")
    print(f"API Key:      {'***' + api_key[-8:] if api_key else 'Not set'}")
    print(f"Project ID:   {project_id or 'Not set'}")
    print()

    if api_key:
        # Try to fetch recent recordings
        try:
            response = client._request("GET", "/telemetry/query", params={"limit": 5})
            recordings = response.get("data", {}).get("recordings", [])

            print("=== Recent Recordings ===\n")
            if recordings:
                for rec in recordings:
                    status = "✓" if rec.get("success") else "✗"
                    print(f"  {status} {rec.get('name')} - {rec.get('source')} - {rec.get('duration', 0):.1f}s")
            else:
                print("  No recordings found")
            print()
        except Exception as e:
            print(f"Could not fetch recordings: {e}")
    else:
        print("Set FFT_API_KEY or ATE_API_KEY to enable telemetry uploads.")


def _handle_upload(args, client) -> None:
    """Upload a telemetry file."""
    filepath = Path(args.file)
    if not filepath.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    # Detect format
    format = args.format
    if format == "auto":
        ext = filepath.suffix.lower()
        if ext == ".json":
            format = "json"
        elif ext in [".mcap", ".bag"]:
            format = "mcap"
        elif ext in [".h5", ".hdf5"]:
            format = "hdf5"
        else:
            print(f"Error: Could not detect format. Use --format to specify.", file=sys.stderr)
            sys.exit(1)

    print(f"Uploading {filepath} ({format} format)...")

    # Load recording
    try:
        if format == "json":
            with open(filepath) as f:
                data = json.load(f)

            # Build recording from JSON
            recording_data = data.get("recording") or data
            if args.robot_id:
                recording_data["robotId"] = args.robot_id
            if args.skill_id:
                recording_data["skillId"] = args.skill_id

        elif format == "mcap":
            from .formats.mcap_serializer import deserialize_from_mcap
            with open(filepath, "rb") as f:
                mcap_data = f.read()
            recording = deserialize_from_mcap(mcap_data)
            recording_data = recording.to_dict()

        elif format == "hdf5":
            from .formats.hdf5_serializer import deserialize_from_hdf5
            with open(filepath, "rb") as f:
                hdf5_data = f.read()
            recording = deserialize_from_hdf5(hdf5_data)
            recording_data = recording.to_dict()

        # Add tags if specified
        if args.tags:
            tags = [t.strip() for t in args.tags.split(",")]
            if "metadata" not in recording_data:
                recording_data["metadata"] = {}
            recording_data["metadata"]["tags"] = tags

        # Upload
        response = client._request("POST", "/telemetry/ingest", json={
            "recording": recording_data,
            "projectId": args.project_id,
        })

        result = response.get("data", {})
        print(f"\n✓ Uploaded successfully!")
        print(f"  Artifact ID: {result.get('artifactId')}")
        print(f"  Frames: {result.get('frameCount')}")
        print(f"  Duration: {result.get('duration', 0):.2f}s")

    except Exception as e:
        print(f"Error uploading: {e}", file=sys.stderr)
        sys.exit(1)


def _handle_export(args, client) -> None:
    """Download and export telemetry."""
    print(f"Downloading artifact {args.artifact_id}...")

    try:
        response = client._request("GET", f"/telemetry/recordings/{args.artifact_id}")
        data = response.get("data", {})

        if not data:
            print(f"Error: Artifact not found", file=sys.stderr)
            sys.exit(1)

        # Build output path
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"telemetry_{args.artifact_id}.{args.format}"
        output_path = output_dir / filename

        # Export to requested format
        if args.format == "json":
            with open(output_path, "w") as f:
                json.dump(data, f, indent=2, default=str)
        elif args.format == "csv":
            # Simple CSV export of key metrics
            import csv
            with open(output_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["id", "robotId", "skillId", "source", "success", "duration", "frameCount"])
                writer.writerow([
                    data.get("id"),
                    data.get("robotId"),
                    data.get("skillId"),
                    data.get("source"),
                    data.get("success"),
                    data.get("duration"),
                    data.get("frameCount"),
                ])
        else:
            print(f"Format {args.format} export not yet implemented for remote data")
            sys.exit(1)

        print(f"✓ Exported to {output_path}")

    except Exception as e:
        print(f"Error exporting: {e}", file=sys.stderr)
        sys.exit(1)


def _handle_list(args, client) -> None:
    """List telemetry recordings."""
    params = {
        "limit": args.limit,
    }
    if args.robot_id:
        params["robotId"] = args.robot_id
    if args.skill_id:
        params["skillId"] = args.skill_id
    if args.source:
        params["source"] = args.source
    if args.success is not None:
        params["success"] = str(args.success).lower()

    try:
        response = client._request("GET", "/telemetry/query", params=params)
        data = response.get("data", {})
        recordings = data.get("recordings", [])

        if args.format == "json":
            print(json.dumps(recordings, indent=2, default=str))
        else:
            # Table format
            print(f"\n{'ID':<15} {'Robot':<15} {'Skill':<15} {'Source':<12} {'Status':<8} {'Duration':<10} {'Frames':<8}")
            print("-" * 95)

            for rec in recordings:
                status = "✓" if rec.get("success") else "✗"
                print(
                    f"{rec.get('id', '')[:14]:<15} "
                    f"{rec.get('robotId', '')[:14]:<15} "
                    f"{(rec.get('skillId') or '-')[:14]:<15} "
                    f"{rec.get('source', ''):<12} "
                    f"{status:<8} "
                    f"{rec.get('duration', 0):.1f}s{'':<5} "
                    f"{rec.get('frameCount', 0):<8}"
                )

            print(f"\nTotal: {data.get('total', len(recordings))} recordings")

    except Exception as e:
        print(f"Error listing recordings: {e}", file=sys.stderr)
        sys.exit(1)


def _handle_agent(args) -> None:
    """Start the fleet telemetry agent."""
    print(f"Starting fleet telemetry agent for robot: {args.robot_id}")
    print(f"Collection frequency: {args.collection_hz} Hz")
    print(f"Upload interval: {args.upload_interval}s")

    if args.daemon:
        print("Running as daemon...")

    asyncio.run(run_fleet_agent(
        robot_id=args.robot_id,
        api_key=args.api_key,
        collection_hz=args.collection_hz,
        upload_interval=args.upload_interval,
        daemon=args.daemon,
    ))


def _handle_record(args, client) -> None:
    """Record telemetry from stdin."""
    print(f"Recording telemetry for robot: {args.robot_id}")
    print("Reading from stdin... (Ctrl+C to stop)")

    collector = TelemetryCollector(
        robot_id=args.robot_id,
        auto_upload=args.output is None,
    )

    collector.start_recording(
        skill_id=args.skill_id,
        source="hardware",
    )

    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)

                # Extract joint positions from various formats
                joint_positions = {}
                if "positions" in data:
                    joint_positions = data["positions"]
                elif "joint_positions" in data:
                    joint_positions = data["joint_positions"]
                elif "qpos" in data:
                    qpos = data["qpos"]
                    joint_positions = {f"joint_{i}": v for i, v in enumerate(qpos)}

                if joint_positions:
                    collector.record_frame(
                        joint_positions=joint_positions,
                        joint_velocities=data.get("velocities") or data.get("joint_velocities"),
                        joint_torques=data.get("torques") or data.get("joint_torques"),
                    )

            except json.JSONDecodeError:
                continue

    except KeyboardInterrupt:
        print("\nStopping recording...")

    recording = collector.stop_recording(success=True)

    if args.output:
        # Save to file
        collector.export_to_file(recording, args.output, args.format)
        print(f"✓ Saved to {args.output}")
    else:
        print(f"✓ Uploaded {recording.metadata.total_frames} frames")

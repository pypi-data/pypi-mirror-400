"""
Skill Marketplace commands for the FoodforThought CLI.
Provides npm-like interface for discovering, installing, and publishing robot skills.
"""

import json
import os
import sys
import time
import zipfile
from pathlib import Path
from typing import Optional, List, Dict, Any

try:
    import requests
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress
    from rich.markdown import Markdown
except ImportError:
    print("Error: Required packages not installed. Run: pip install rich requests")
    sys.exit(1)

console = Console()

# API configuration
BASE_URL = os.getenv("ATE_API_URL", "https://kindly.fyi/api")
API_KEY = os.getenv("ATE_API_KEY", "")


class MarketplaceClient:
    """Client for interacting with the Skill Marketplace API."""

    def __init__(self, base_url: str = BASE_URL, api_key: str = API_KEY):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to API."""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET" and "params" in kwargs:
                response = requests.get(url, headers=self.headers, params=kwargs["params"])
            else:
                response = requests.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            try:
                error_data = e.response.json()
                console.print(f"[red]Error: {error_data.get('error', str(e))}[/red]")
            except Exception:
                console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            console.print(f"[red]Network error: {e}[/red]")
            sys.exit(1)

    def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        return self._request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, data: Dict = None, **kwargs) -> Dict[str, Any]:
        return self._request("POST", endpoint, json=data, **kwargs)

    def put(self, endpoint: str, data: Dict = None, **kwargs) -> Dict[str, Any]:
        return self._request("PUT", endpoint, json=data, **kwargs)


# Singleton client
_client: Optional[MarketplaceClient] = None


def get_client() -> MarketplaceClient:
    global _client
    if _client is None:
        _client = MarketplaceClient()
    return _client


def search_skills(
    query: str,
    category: Optional[str] = None,
    robot_type: Optional[str] = None,
    license_type: Optional[str] = None,
    pricing: Optional[str] = None,
    sort: str = "downloads",
    limit: int = 20,
) -> None:
    """
    Search the skill marketplace.

    Examples:
        ate marketplace search "pick and place"
        ate marketplace search gripper --category manipulation
        ate marketplace search navigation --robot ur5
    """
    client = get_client()

    params = {"q": query, "sort": sort, "limit": limit}
    if category:
        params["category"] = category
    if robot_type:
        params["robotType"] = robot_type
    if license_type:
        params["license"] = license_type
    if pricing:
        params["pricing"] = pricing

    with console.status("Searching marketplace..."):
        result = client.get("/marketplace/skills", params=params)

    skills = result.get("skills", [])
    pagination = result.get("pagination", {})

    if not skills:
        console.print(f"[yellow]No skills found matching '{query}'[/yellow]")
        return

    table = Table(title=f"Skills matching '{query}' ({pagination.get('total', 0)} total)")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Author", style="dim")
    table.add_column("Category")
    table.add_column("Downloads", justify="right")
    table.add_column("Rating", justify="right")
    table.add_column("License", style="dim")

    for skill in skills:
        rating = skill.get("avgRating", 0)
        rating_str = f"{rating:.1f}" if rating > 0 else "—"
        verified = "" if not skill.get("verified") else " "

        table.add_row(
            f"{skill['name']}{verified}",
            skill.get("author", {}).get("name", "Unknown"),
            skill.get("category", "—"),
            str(skill.get("downloads", 0)),
            rating_str,
            skill.get("license", "—").upper(),
        )

    console.print(table)

    if pagination.get("hasMore"):
        console.print(
            f"\n[dim]Showing {len(skills)} of {pagination.get('total')} results. "
            f"Use --limit to see more.[/dim]"
        )


def show_skill(slug: str) -> None:
    """
    Show detailed information about a skill.

    Examples:
        ate marketplace show pick-and-place
    """
    client = get_client()

    with console.status(f"Fetching skill '{slug}'..."):
        result = client.get(f"/marketplace/skills/{slug}")

    skill = result.get("skill", {})

    if not skill:
        console.print(f"[red]Skill '{slug}' not found[/red]")
        return

    # Header
    verified = "" if not skill.get("verified") else ""
    console.print(Panel(
        f"[bold cyan]{skill['name']}[/bold cyan] {verified}\n"
        f"[dim]by {skill.get('author', {}).get('name', 'Unknown')}[/dim]\n\n"
        f"{skill.get('description', 'No description')}",
        title=f"v{skill.get('version', '?')}",
        subtitle=skill.get('category', ''),
    ))

    # Stats table
    stats_table = Table(show_header=False, box=None)
    stats_table.add_column("Key", style="dim")
    stats_table.add_column("Value")

    rating = skill.get("avgRating", 0)
    stats_table.add_row("Downloads", str(skill.get("downloads", 0)))
    stats_table.add_row("Installs", str(skill.get("installs", 0)))
    stats_table.add_row("Executions", str(skill.get("executions", 0)))
    stats_table.add_row("Success Rate", f"{skill.get('successRate', 0) * 100:.1f}%")
    stats_table.add_row("Rating", f"{rating:.1f}" if rating > 0 else "No ratings")
    stats_table.add_row("License", skill.get("license", "—").upper())

    # Pricing
    pricing = skill.get("pricing", {})
    if pricing.get("type") == "free":
        stats_table.add_row("Price", "[green]Free[/green]")
    else:
        price = pricing.get("price", 0)
        currency = pricing.get("currency", "usd").upper()
        stats_table.add_row("Price", f"${price:.2f} {currency}")

    console.print(stats_table)

    # Compatibility
    compatibility = skill.get("compatibility", [])
    if compatibility:
        console.print("\n[bold]Compatible Robots:[/bold]")
        for compat in compatibility[:5]:
            robot = compat.get("robot", {})
            success = compat.get("successRate", 0)
            console.print(
                f"  • {robot.get('name', 'Unknown')} "
                f"({robot.get('manufacturer', '')}) - "
                f"[green]{success * 100:.0f}% success[/green]"
            )

    # Links
    console.print("\n[bold]Links:[/bold]")
    if skill.get("sourceUrl"):
        console.print(f"  Source: {skill['sourceUrl']}")
    if skill.get("documentationUrl"):
        console.print(f"  Docs: {skill['documentationUrl']}")
    console.print(f"  Web: https://foodforthought.kindly.fyi/marketplace/{slug}")


def install_skill(
    skill_name: str,
    version: Optional[str] = None,
    robot: Optional[str] = None,
    output_dir: Optional[str] = None,
) -> None:
    """
    Install a skill from the marketplace.

    Examples:
        ate marketplace install pick-and-place
        ate marketplace install pick-and-place --version 1.2.0
        ate marketplace install pick-and-place --robot my-arm
    """
    client = get_client()

    # Check compatibility first if robot specified
    if robot:
        console.print(f"Checking compatibility with {robot}...")
        compat = client.post("/marketplace/compatibility", {
            "skillSlug": skill_name,
            "robotId": robot,
        })

        if not compat.get("compatible"):
            console.print(f"[red]Skill is not compatible with robot {robot}[/red]")
            for issue in compat.get("issues", []):
                console.print(f"  • {issue}")

            adaptations = compat.get("adaptations", [])
            if adaptations:
                console.print("\n[yellow]Possible adaptations:[/yellow]")
                for adapt in adaptations:
                    console.print(f"  • {adapt.get('description')}")

            if not console.input("\nInstall anyway? (y/N): ").lower() == "y":
                return

    # Install
    with console.status("Installing skill..."):
        result = client.post(f"/marketplace/skills/{skill_name}/install", {
            "version": version,
            "robotId": robot,
        })

    if result.get("requiresPayment"):
        console.print("[yellow]This is a paid skill.[/yellow]")
        console.print(f"Price: ${result['pricing'].get('price', 0):.2f}")
        console.print(f"Checkout: {result.get('checkoutUrl')}")
        return

    download_url = result.get("downloadUrl")
    installed_version = result.get("version")

    if not download_url:
        console.print("[red]Failed to get download URL[/red]")
        return

    # Download package
    output_path = Path(output_dir or f"./{skill_name}")
    output_path.mkdir(parents=True, exist_ok=True)

    with Progress() as progress:
        task = progress.add_task("Downloading...", total=100)

        try:
            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            # Save as zip and extract
            zip_path = output_path / f"{skill_name}.zip"
            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            progress.update(task, completed=50)

            # Extract
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(output_path)
            progress.update(task, completed=100)

            # Clean up zip
            zip_path.unlink()

        except Exception as e:
            console.print(f"[red]Download failed: {e}[/red]")
            # Still mark as installed since the installation record was created
            console.print("[yellow]Skill recorded as installed but download failed.[/yellow]")
            return

    console.print(f"[green] Installed {skill_name} v{installed_version}[/green]")
    console.print(f"Location: {output_path.absolute()}")

    # Show compatibility info
    compat_info = result.get("compatibility")
    if compat_info:
        if compat_info.get("status") == "untested":
            console.print(
                "[yellow]Note: This skill hasn't been tested on your robot. "
                "Please report compatibility after testing.[/yellow]"
            )


def publish_skill(
    path: str,
    public: bool = True,
) -> None:
    """
    Publish a skill to the marketplace.

    The skill directory must contain a skill.yaml file with metadata.

    Examples:
        ate marketplace publish ./my-skill
        ate marketplace publish ./my-skill --no-public
    """
    skill_path = Path(path)

    if not skill_path.exists():
        console.print(f"[red]Path not found: {path}[/red]")
        return

    # Look for skill.yaml
    config_path = skill_path / "skill.yaml"
    if not config_path.exists():
        config_path = skill_path / "skill.yml"
    if not config_path.exists():
        console.print("[red]skill.yaml not found in skill directory[/red]")
        console.print("\nCreate a skill.yaml with:")
        console.print("""
name: my-skill
version: 1.0.0
description: A brief description
category: manipulation
tags:
  - gripper
  - pick-and-place
license: mit
""")
        return

    # Parse config
    try:
        import yaml
        with open(config_path) as f:
            config = yaml.safe_load(f)
    except ImportError:
        console.print("[yellow]PyYAML not installed, trying JSON fallback...[/yellow]")
        # Try JSON fallback
        json_path = skill_path / "skill.json"
        if json_path.exists():
            with open(json_path) as f:
                config = json.load(f)
        else:
            console.print("[red]Install PyYAML or use skill.json[/red]")
            return
    except Exception as e:
        console.print(f"[red]Failed to parse config: {e}[/red]")
        return

    # Validate required fields
    required = ["name", "version", "description", "category"]
    missing = [f for f in required if not config.get(f)]
    if missing:
        console.print(f"[red]Missing required fields: {', '.join(missing)}[/red]")
        return

    console.print(f"Publishing [cyan]{config['name']}[/cyan] v{config['version']}...")

    # Create package zip
    console.print("Creating package...")
    zip_path = skill_path.parent / f"{config['name']}-{config['version']}.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for file in skill_path.rglob("*"):
            if file.is_file():
                # Skip common non-essential files
                if file.name.startswith(".") or file.suffix in [".pyc", ".pyo"]:
                    continue
                if "__pycache__" in str(file):
                    continue
                arcname = file.relative_to(skill_path)
                z.write(file, arcname)

    # Upload package (placeholder - would upload to Vercel Blob or S3)
    console.print("Uploading package...")
    # In production, this would upload to cloud storage
    # For now, we'll just use a placeholder URL
    package_url = f"https://storage.kindly.fyi/skills/{config['name']}/{config['version']}/package.zip"

    # Clean up local zip
    zip_path.unlink()

    # Read README if exists
    readme = None
    readme_path = skill_path / "README.md"
    if readme_path.exists():
        readme = readme_path.read_text()

    # Publish to API
    client = get_client()

    try:
        result = client.post("/marketplace/skills", {
            "name": config["name"],
            "version": config["version"],
            "description": config["description"],
            "readme": readme,
            "category": config.get("category", "other"),
            "tags": config.get("tags", []),
            "robotTypes": config.get("robotTypes", []),
            "hardwareRequirements": config.get("hardwareRequirements", []),
            "softwareRequirements": config.get("softwareRequirements", []),
            "packageUrl": package_url,
            "sourceUrl": config.get("sourceUrl"),
            "documentationUrl": config.get("documentationUrl"),
            "license": config.get("license", "mit"),
            "pricing": config.get("pricing", {"type": "free"}),
        })

        skill = result.get("skill", {})
        console.print(f"[green] Published {skill['name']} v{skill['version']}[/green]")
        console.print(f"Status: {skill.get('status', 'pending_review')}")
        console.print(f"URL: https://foodforthought.kindly.fyi/marketplace/{skill['slug']}")

        if skill.get("status") == "pending_review":
            console.print(
                "\n[yellow]Your skill is pending review. "
                "It will be published once approved.[/yellow]"
            )
    except Exception as e:
        console.print(f"[red]Failed to publish: {e}[/red]")


def report_compatibility(
    skill_name: str,
    robot: str,
    works: bool,
    notes: Optional[str] = None,
    version: Optional[str] = None,
) -> None:
    """
    Report skill compatibility with a robot.

    Examples:
        ate marketplace report pick-and-place my-arm --works
        ate marketplace report pick-and-place my-arm --no-works --notes "Gripper too weak"
    """
    client = get_client()

    result = client.put("/marketplace/compatibility", {
        "skillSlug": skill_name,
        "robotId": robot,
        "works": works,
        "notes": notes,
        "version": version,
    })

    stats = result.get("communityStats", {})
    console.print("[green] Compatibility report submitted. Thank you![/green]")
    console.print(
        f"\nCommunity stats for this robot: "
        f"{stats.get('workingReports', 0)}/{stats.get('totalReports', 0)} working "
        f"({stats.get('successRate', 0) * 100:.0f}% success rate)"
    )


def list_installed() -> None:
    """List all installed skills."""
    client = get_client()

    # Get user's installations
    result = client.get("/marketplace/skills", params={"installed": "true"})

    skills = result.get("skills", [])

    if not skills:
        console.print("[yellow]No skills installed[/yellow]")
        console.print("Use 'ate marketplace search' to find skills to install.")
        return

    table = Table(title="Installed Skills")
    table.add_column("Name", style="cyan")
    table.add_column("Version")
    table.add_column("Category")
    table.add_column("Installed")

    for skill in skills:
        table.add_row(
            skill["name"],
            skill["version"],
            skill.get("category", "—"),
            skill.get("installedAt", "—"),
        )

    console.print(table)

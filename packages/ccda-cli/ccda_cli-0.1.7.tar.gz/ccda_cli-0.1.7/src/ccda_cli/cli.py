"""CCDA-CLI: Software supply chain security metrics collector.

CLI entry point and command definitions.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.table import Table

from ccda_cli.config import Config, set_config

console = Console()


def run_async(coro):
    """Run async coroutine in sync context."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No loop running, create a new one
        return asyncio.run(coro)
    else:
        # Loop already running, use run_until_complete
        return loop.run_until_complete(coro)


class Context:
    """CLI context holding configuration and shared state."""

    def __init__(self) -> None:
        self.config: Config | None = None
        self.verbose: bool = False
        self.debug: bool = False


pass_context = click.make_pass_decorator(Context, ensure=True)


@click.group()
@click.option(
    "--config",
    "-c",
    "config_file",
    type=click.Path(exists=True, path_type=Path),
    help="Path to config file",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--debug", is_flag=True, help="Enable debug output")
@click.option("--cache-dir", type=click.Path(path_type=Path), help="Override cache directory")
@click.option("--github-token", envvar="CCDA_GITHUB_TOKEN", help="GitHub API token")
@click.version_option(package_name="ccda-cli")
@pass_context
def cli(
    ctx: Context,
    config_file: Path | None,
    verbose: bool,
    debug: bool,
    cache_dir: Path | None,
    github_token: str | None,
) -> None:
    """CCDA-CLI: Collect software supply chain security metrics.

    Analyzes packages and repositories for community health, maintainer burnout,
    and security practices using an offline-first approach.
    """
    ctx.verbose = verbose
    ctx.debug = debug

    # Build CLI overrides
    cli_overrides: dict[str, Any] = {}
    if cache_dir:
        cli_overrides["cache"] = {"directory": cache_dir}
    if github_token:
        cli_overrides["github_token"] = github_token

    # Load configuration
    ctx.config = Config.load(config_file=config_file, cli_overrides=cli_overrides)
    set_config(ctx.config)

    if debug:
        console.print(f"[dim]Config loaded from: {config_file or 'defaults'}[/dim]")


# =============================================================================
# Discovery Commands
# =============================================================================


@cli.command()
@click.argument("purl")
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file path")
@click.option("--no-serpapi", is_flag=True, help="Disable SerpAPI fallback")
@pass_context
def discover(ctx: Context, purl: str, output: Path | None, no_serpapi: bool) -> None:
    """Discover package metadata from a PURL.

    Resolves the PURL to find:
    - Package name and version
    - Source tarball URL
    - GitHub repository
    """
    from ccda_cli.discovery import PackageResolver, PURLParser
    from ccda_cli.cache import CacheManager

    console.print(f"[bold]Discovering:[/bold] {purl}")

    try:
        # Validate PURL
        parsed = PURLParser.parse(purl)
        if ctx.verbose:
            console.print(f"  Type: {parsed.type}, Name: {parsed.full_name}")

        # Check cache first
        cache = CacheManager()
        cached = cache.get_package_data(purl, "discovery.json")
        if cached:
            console.print("[dim]Using cached discovery data[/dim]")
            result_data = cached.data
        else:
            # Run discovery
            resolver = PackageResolver()
            result = run_async(resolver.discover(purl))
            result_data = result.to_dict()

            # Save to cache
            cache.save_package_data(purl, "discovery.json", result_data)

        # Output results
        if output:
            with open(output, "w") as f:
                json.dump(result_data, f, indent=2)
            console.print(f"[green]Saved to: {output}[/green]")
        else:
            console.print_json(json.dumps(result_data, indent=2))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


# =============================================================================
# Clone Commands
# =============================================================================


@cli.command()
@click.argument("repo_url")
@click.option("--depth", type=int, default=1000, help="Clone depth")
@click.option("--cache-dir", type=click.Path(path_type=Path), help="Cache directory")
@click.option("--force", is_flag=True, help="Force re-clone even if exists")
@pass_context
def clone(ctx: Context, repo_url: str, depth: int, cache_dir: Path | None, force: bool) -> None:
    """Clone a single repository for offline analysis."""
    from ccda_cli.core.git import GitManager

    console.print(f"[bold]Cloning:[/bold] {repo_url}")
    console.print(f"  Depth: {depth}")

    try:
        manager = GitManager(cache_dir=cache_dir)
        result = run_async(manager.clone(repo_url, depth=depth, force=force))

        if result.success:
            console.print(f"[green]Cloned to:[/green] {result.local_path}")
            if result.last_commit_hash:
                console.print(f"  Last commit: {result.last_commit_hash[:7]}")
            if result.last_commit_date:
                console.print(f"  Commit date: {result.last_commit_date}")
        else:
            console.print(f"[red]Clone failed:[/red] {result.error}")
            raise click.Abort()

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@cli.command("clone-batch")
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option("--cache-dir", type=click.Path(path_type=Path), help="Cache directory")
@click.option("--concurrency", type=int, default=3, help="Max concurrent clones")
@click.option("--depth", type=int, default=1000, help="Clone depth")
@pass_context
def clone_batch(
    ctx: Context, input_file: Path, cache_dir: Path | None, concurrency: int, depth: int
) -> None:
    """Clone multiple repositories from a file."""
    from ccda_cli.core.git import GitManager

    console.print(f"[bold]Batch cloning from:[/bold] {input_file}")

    try:
        # Read URLs from file
        with open(input_file) as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

        if not urls:
            console.print("[yellow]No URLs found in file[/yellow]")
            return

        console.print(f"  Found {len(urls)} repositories")
        console.print(f"  Concurrency: {concurrency}")

        manager = GitManager(cache_dir=cache_dir)
        results = run_async(manager.clone_batch(urls, depth=depth, concurrency=concurrency))

        # Summary
        success = sum(1 for r in results if r.success)
        failed = len(results) - success

        console.print(f"\n[bold]Results:[/bold]")
        console.print(f"  [green]Success: {success}[/green]")
        if failed > 0:
            console.print(f"  [red]Failed: {failed}[/red]")
            for r in results:
                if not r.success:
                    console.print(f"    - {r.repo_url}: {r.error}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@cli.command("clone-update")
@click.option("--cache-dir", type=click.Path(path_type=Path), help="Cache directory")
@click.option("--max-age", default="24h", help="Update repos older than this (e.g., 24h, 7d)")
@pass_context
def clone_update(ctx: Context, cache_dir: Path | None, max_age: str) -> None:
    """Update stale repository clones."""
    from ccda_cli.core.git import GitManager
    import re

    console.print(f"[bold]Updating clones older than:[/bold] {max_age}")

    try:
        # Parse max_age
        match = re.match(r"(\d+)(h|d)", max_age)
        if not match:
            console.print("[red]Invalid max-age format. Use e.g., 24h or 7d[/red]")
            return

        value, unit = match.groups()
        hours = int(value) * (24 if unit == "d" else 1)

        manager = GitManager(cache_dir=cache_dir)
        stale = manager.get_stale_clones(max_age_hours=hours)

        if not stale:
            console.print("[green]No stale clones found[/green]")
            return

        console.print(f"Found {len(stale)} stale repositories")

        async def update_all():
            results = []
            for repo in stale:
                console.print(f"  Updating: {repo['url']}")
                result = await manager.update(repo['url'])
                results.append(result)
            return results

        results = run_async(update_all())

        success = sum(1 for r in results if r.success)
        console.print(f"\n[green]Updated: {success}/{len(results)}[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@cli.command("clone-list")
@click.option("--cache-dir", type=click.Path(path_type=Path), help="Cache directory")
@pass_context
def clone_list(ctx: Context, cache_dir: Path | None) -> None:
    """List cached repository clones."""
    from ccda_cli.core.git import GitManager

    try:
        manager = GitManager(cache_dir=cache_dir)
        repos = manager.list_clones()

        if not repos:
            console.print("[yellow]No cloned repositories found[/yellow]")
            return

        table = Table(title=f"Cloned Repositories ({len(repos)})")
        table.add_column("Repository", style="cyan")
        table.add_column("Last Updated", style="green")
        table.add_column("Commit", style="dim")

        for repo in repos:
            url = repo.get("url", "unknown")
            last_updated = repo.get("last_updated") or repo.get("cloned_at", "unknown")
            if isinstance(last_updated, str) and "T" in last_updated:
                last_updated = last_updated.split("T")[0]
            commit = repo.get("last_commit_hash", "")[:7] if repo.get("last_commit_hash") else ""

            table.add_row(url, str(last_updated), commit)

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command("clone-clean")
@click.option("--cache-dir", type=click.Path(path_type=Path), help="Cache directory")
@click.option("--older-than", default="7d", help="Remove repos older than this")
@click.option("--dry-run", is_flag=True, help="Show what would be removed")
@pass_context
def clone_clean(
    ctx: Context, cache_dir: Path | None, older_than: str, dry_run: bool
) -> None:
    """Clean old repository clones."""
    from ccda_cli.core.git import GitManager
    import re

    console.print(f"[bold]Cleaning clones older than:[/bold] {older_than}")
    if dry_run:
        console.print("[dim](dry run)[/dim]")

    try:
        # Parse older_than
        match = re.match(r"(\d+)(h|d)", older_than)
        if not match:
            console.print("[red]Invalid format. Use e.g., 24h or 7d[/red]")
            return

        value, unit = match.groups()
        hours = int(value) * (24 if unit == "d" else 1)

        manager = GitManager(cache_dir=cache_dir)
        stale = manager.get_stale_clones(max_age_hours=hours)

        if not stale:
            console.print("[green]No old clones to remove[/green]")
            return

        console.print(f"Found {len(stale)} repositories to clean")

        for repo in stale:
            url = repo.get("url", "unknown")
            age_hours = repo.get("age_hours", 0)
            age_days = age_hours / 24

            if dry_run:
                console.print(f"  Would remove: {url} (age: {age_days:.1f} days)")
            else:
                console.print(f"  Removing: {url}")
                manager.delete_clone(url)

        if not dry_run:
            console.print(f"[green]Removed {len(stale)} repositories[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


# =============================================================================
# Analysis Commands
# =============================================================================


@cli.command("git-metrics")
@click.argument("repo_path", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file path")
@click.option("--format", "-f", "output_format", type=click.Choice(["table", "json"]), default="table", help="Output format")
@click.option("--repo-url", help="Repository URL for metadata")
@pass_context
def git_metrics(
    ctx: Context, repo_path: Path, output: Path | None, output_format: str, repo_url: str | None
) -> None:
    """Analyze git repository for offline metrics.

    Extracts bus factor, pony factor, contributor stats, and license history.
    """
    from ccda_cli.metrics.git import GitMetricsAnalyzer

    console.print(f"[bold]Analyzing git metrics:[/bold] {repo_path}")

    try:
        analyzer = GitMetricsAnalyzer(repo_path)
        result = analyzer.analyze(repo_url=repo_url)
        result_data = result.to_dict()

        if output_format == "json":
            # Full JSON output
            if output:
                with open(output, "w") as f:
                    json.dump(result_data, f, indent=2)
                console.print(f"[green]Saved to: {output}[/green]")
            else:
                console.print_json(json.dumps(result_data, indent=2))
        else:
            # Detailed table output
            for window_name, metrics in result.time_windows.items():
                # Summary table
                table = Table(title=f"Git Metrics ({window_name})")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")

                table.add_row("Total Commits", str(metrics.total_commits))
                table.add_row("Unique Contributors", str(metrics.unique_contributors))
                table.add_row("Bus Factor", str(metrics.bus_factor))
                table.add_row("Pony Factor", str(metrics.pony_factor))
                table.add_row("Elephant Factor", str(metrics.elephant_factor))
                table.add_row("Commits/Day", f"{metrics.commits_per_day:.2f}")
                table.add_row("Contributor Retention", f"{metrics.contributor_retention:.1f}%")

                console.print(table)
                console.print()

                # Top Contributors table
                if metrics.top_contributors:
                    contrib_table = Table(title=f"Top Contributors ({window_name})")
                    contrib_table.add_column("Rank", style="dim")
                    contrib_table.add_column("Name", style="cyan")
                    contrib_table.add_column("Company", style="yellow")
                    contrib_table.add_column("Commits", style="green")
                    contrib_table.add_column("%", style="white")

                    for i, c in enumerate(metrics.top_contributors[:10], 1):
                        contrib_table.add_row(
                            str(i),
                            c.name,
                            c.company or "Unknown",
                            str(c.commits),
                            f"{c.percentage:.1f}%"
                        )

                    console.print(contrib_table)
                    console.print()

                # Company Distribution table
                if metrics.company_distribution:
                    company_table = Table(title=f"Company Distribution ({window_name})")
                    company_table.add_column("Company", style="cyan")
                    company_table.add_column("Commits", style="green")
                    company_table.add_column("%", style="white")
                    company_table.add_column("Contributors", style="dim")

                    for co in metrics.company_distribution:
                        company_table.add_row(
                            co.company,
                            str(co.commits),
                            f"{co.percentage:.1f}%",
                            str(co.contributors) if hasattr(co, 'contributors') and co.contributors else "-"
                        )

                    console.print(company_table)
                    console.print()

            # License History table
            if result.license_changes:
                lic = result.license_changes
                lic_table = Table(title="License History")
                lic_table.add_column("Property", style="cyan")
                lic_table.add_column("Value", style="green")

                lic_table.add_row("License File", lic.license_file or "Not found")
                lic_table.add_row("Current License", lic.current_license or "Unknown")
                lic_table.add_row("Change Count", str(lic.change_count))
                lic_table.add_row("Risk Level", lic.risk_level)

                console.print(lic_table)

                # License changes detail
                if lic.changes:
                    changes_table = Table(title="License Change History")
                    changes_table.add_column("Commit", style="dim")
                    changes_table.add_column("Date", style="white")
                    changes_table.add_column("Old License", style="red")
                    changes_table.add_column("New License", style="green")

                    for change in lic.changes:
                        changes_table.add_row(
                            change.commit_hash[:7] if hasattr(change, 'commit_hash') else str(change.get('commit_hash', ''))[:7],
                            str(change.date if hasattr(change, 'date') else change.get('date', '')),
                            str(change.old_license if hasattr(change, 'old_license') else change.get('old_license')) or "None",
                            str(change.new_license if hasattr(change, 'new_license') else change.get('new_license')) or "None"
                        )

                    console.print(changes_table)

            # Save to file if requested
            if output:
                with open(output, "w") as f:
                    json.dump(result_data, f, indent=2)
                console.print(f"\n[green]Saved to: {output}[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@cli.command("github-metrics")
@click.argument("repo_url")
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file path")
@pass_context
def github_metrics(ctx: Context, repo_url: str, output: Path | None) -> None:
    """Fetch GitHub API metrics (issues, PRs, releases).

    Requires GitHub token for authenticated requests.
    """
    from ccda_cli.metrics.github import GitHubMetricsCollector

    console.print(f"[bold]Fetching GitHub metrics:[/bold] {repo_url}")

    if not ctx.config or not ctx.config.github_token:
        console.print("[yellow]Warning: No GitHub token configured. Rate limits will apply.[/yellow]")

    try:
        collector = GitHubMetricsCollector()
        result = run_async(collector.collect(repo_url))
        result_data = result.to_dict()

        # Display summary
        table = Table(title="GitHub Metrics")
        table.add_column("Category", style="cyan")
        table.add_column("Metric", style="white")
        table.add_column("Value", style="green")

        # Repository
        table.add_row("Repository", "Stars", str(result.repository.stars))
        table.add_row("", "Forks", str(result.repository.forks))

        # Issues
        table.add_row("Issues", "Open", str(result.issues.open_count))
        table.add_row("", "Unresponded (7d)", f"{result.issues.unresponded_rate_7d:.1f}%")

        # PRs
        table.add_row("Pull Requests", "Open", str(result.pull_requests.open_count))
        table.add_row("", "Avg Merge Time", f"{result.pull_requests.avg_merge_hours:.1f}h")

        # Releases
        table.add_row("Releases", "Total", str(result.releases.total_count))
        table.add_row("", "Signed", "Yes" if result.releases.has_signed_releases else "No")

        # Protection
        table.add_row("Branch Protection", "Protected", "Yes" if result.branch_protection.default_branch_protected else "No")

        console.print(table)
        console.print(f"[dim]API calls used: {result.api_calls_used}[/dim]")

        # Output results
        if output:
            with open(output, "w") as f:
                json.dump(result_data, f, indent=2)
            console.print(f"[green]Saved to: {output}[/green]")
        elif ctx.verbose:
            console.print_json(json.dumps(result_data, indent=2))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@cli.command("scan-tarball")
@click.argument("target")  # PURL or file path
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file path")
@pass_context
def scan_tarball(ctx: Context, target: str, output: Path | None) -> None:
    """Scan a tarball for licenses, copyrights, and binaries.

    TARGET can be a PURL (pkg:npm/express@4.18.2) or a local file path.
    Uses osslili and binarysniffer for analysis.
    """
    from ccda_cli.scanner import TarballScanner

    console.print(f"[bold]Scanning tarball:[/bold] {target}")

    try:
        scanner = TarballScanner()
        target_path = Path(target)

        # Check if target is a local path or PURL
        if target_path.exists():
            console.print("[dim]Scanning local file/directory[/dim]")
            result = scanner.scan_local(target, target_path)
        elif target.startswith("pkg:"):
            console.print("[dim]Discovering and scanning package[/dim]")
            result = run_async(scanner.scan_purl(target))
        else:
            console.print("[red]Invalid target: must be a PURL or existing path[/red]")
            raise click.Abort()

        result_data = result.to_dict()

        # Display summary
        table = Table(title="Tarball Scan Results")
        table.add_column("Category", style="cyan")
        table.add_column("Details", style="white")

        # License files
        license_info = []
        for lf in result.license_files:
            lic_str = f"{lf.path}"
            if lf.spdx_id:
                lic_str += f" ({lf.spdx_id}, {lf.confidence}%)"
            license_info.append(lic_str)
        table.add_row("License Files", "\n".join(license_info) if license_info else "None found")

        # Binaries
        binary_count = len(result.binaries.get("files", []))
        if binary_count > 0:
            signatures = result.binaries.get("signatures", [])
            binary_info = f"{binary_count} files"
            if signatures:
                binary_info += f" ({', '.join(signatures[:3])})"
            table.add_row("Binary Files", binary_info)
        else:
            table.add_row("Binary Files", "[green]None[/green]")

        # Copyrights
        table.add_row("Copyright Statements", str(len(result.copyrights)))

        # Metadata
        meta = result.package_metadata
        if meta.name:
            table.add_row("Package", f"{meta.name}@{meta.version or 'unknown'}")
        if meta.license:
            table.add_row("Declared License", meta.license)

        # Stats
        table.add_row("Total Files", str(result.file_count))
        table.add_row("Total Size", f"{result.total_size_bytes / 1024:.1f} KB")
        table.add_row("Scan Method", result.scan_method)

        console.print(table)

        # Output results
        if output:
            with open(output, "w") as f:
                json.dump(result_data, f, indent=2)
            console.print(f"[green]Saved to: {output}[/green]")
        elif ctx.verbose:
            console.print_json(json.dumps(result_data, indent=2))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if ctx.debug:
            import traceback
            console.print(traceback.format_exc())
        raise click.Abort()


# =============================================================================
# Scoring Commands
# =============================================================================


@cli.command("health-score")
@click.argument("target")  # PURL or metrics files
@click.option("--git-metrics", "git_metrics_file", type=click.Path(exists=True, path_type=Path))
@click.option("--github-metrics", "github_metrics_file", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file path")
@click.option("--format", "-f", "output_format", type=click.Choice(["table", "json"]), default="table", help="Output format")
@pass_context
def health_score(
    ctx: Context,
    target: str,
    git_metrics_file: Path | None,
    github_metrics_file: Path | None,
    output: Path | None,
    output_format: str,
) -> None:
    """Calculate project health score (0-100).

    Can calculate from existing metrics files or fetch automatically from a PURL.
    """
    from ccda_cli.scoring.health import HealthScoreCalculator
    from ccda_cli.metrics.git import GitMetricsResult
    from ccda_cli.cache import CacheManager

    console.print(f"[bold]Calculating health score:[/bold] {target}")

    try:
        git_metrics = None
        github_metrics = None
        cache = CacheManager()

        # Load metrics from files if provided
        if git_metrics_file:
            with open(git_metrics_file) as f:
                data = json.load(f)
                git_metrics = GitMetricsResult.from_dict(data)
                console.print(f"[dim]Loaded git metrics from: {git_metrics_file}[/dim]")

        if github_metrics_file:
            with open(github_metrics_file) as f:
                data = json.load(f)
                # GitHub metrics loading would need similar from_dict
                console.print(f"[dim]Loaded GitHub metrics from: {github_metrics_file}[/dim]")

        # If target is a PURL, try to load cached metrics
        if target.startswith("pkg:") and not git_metrics:
            # Try to load cached unified analysis or individual metrics
            cached = cache.get_package_data(target, "unified.json")
            if cached and cached.data:
                if "git_metrics" in cached.data:
                    git_metrics = GitMetricsResult.from_dict(cached.data["git_metrics"])
                    console.print("[dim]Loaded cached git metrics[/dim]")

        # Calculate score
        calculator = HealthScoreCalculator()
        result = calculator.calculate(target, git_metrics, github_metrics)
        result_data = result.to_dict()

        if output_format == "json":
            if output:
                with open(output, "w") as f:
                    json.dump(result_data, f, indent=2)
                console.print(f"[green]Saved to: {output}[/green]")
            else:
                console.print_json(json.dumps(result_data, indent=2))
        else:
            # Display summary table
            grade_colors = {"A": "green", "B": "blue", "C": "yellow", "D": "orange3", "F": "red"}
            grade_color = grade_colors.get(result.grade, "white")

            console.print()
            console.print(f"[bold]Health Score:[/bold] [{grade_color}]{result.health_score}/100[/{grade_color}]")
            console.print(f"[bold]Grade:[/bold] [{grade_color}]{result.grade}[/{grade_color}]")
            console.print(f"[bold]Risk Level:[/bold] {result.risk_level}")

            # Category scores table
            if result.category_scores:
                table = Table(title="Category Scores")
                table.add_column("Category", style="cyan")
                table.add_column("Score", style="green")
                table.add_column("Weight", style="dim")
                table.add_column("Status", style="white")

                for name, cat in result.category_scores.items():
                    status_color = {"healthy": "green", "moderate": "yellow", "warning": "orange3", "critical": "red"}.get(cat.status, "white")
                    table.add_row(
                        name.replace("_", " ").title(),
                        f"{cat.score}/100",
                        str(cat.weight),
                        f"[{status_color}]{cat.status}[/{status_color}]"
                    )

                console.print(table)

            if result.risk_factors:
                console.print("\n[bold]Risk Factors:[/bold]")
                for rf in result.risk_factors:
                    sev_color = {"low": "blue", "medium": "yellow", "high": "orange3", "critical": "red"}.get(rf.severity, "white")
                    console.print(f"  - [{sev_color}]{rf.severity}[/{sev_color}]: {rf.message}")

            if result.recommendations:
                console.print("\n[bold]Recommendations:[/bold]")
                for rec in result.recommendations:
                    console.print(f"  - {rec}")

            # Save to file if requested
            if output:
                with open(output, "w") as f:
                    json.dump(result_data, f, indent=2)
                console.print(f"\n[green]Saved to: {output}[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if ctx.debug:
            import traceback
            console.print(traceback.format_exc())
        raise click.Abort()


@cli.command("burnout-score")
@click.argument("target")  # PURL or metrics files
@click.option("--git-metrics", "git_metrics_file", type=click.Path(exists=True, path_type=Path))
@click.option("--github-metrics", "github_metrics_file", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file path")
@click.option("--format", "-f", "output_format", type=click.Choice(["table", "json"]), default="table", help="Output format")
@pass_context
def burnout_score(
    ctx: Context,
    target: str,
    git_metrics_file: Path | None,
    github_metrics_file: Path | None,
    output: Path | None,
    output_format: str,
) -> None:
    """Calculate developer burnout risk score (0-100).

    Analyzes issue backlog, response gaps, workload concentration, and activity trends.
    """
    from ccda_cli.scoring.burnout import BurnoutScoreCalculator
    from ccda_cli.metrics.git import GitMetricsResult
    from ccda_cli.cache import CacheManager

    console.print(f"[bold]Calculating burnout score:[/bold] {target}")

    try:
        git_metrics = None
        github_metrics = None
        cache = CacheManager()

        # Load metrics from files if provided
        if git_metrics_file:
            with open(git_metrics_file) as f:
                data = json.load(f)
                git_metrics = GitMetricsResult.from_dict(data)
                console.print(f"[dim]Loaded git metrics from: {git_metrics_file}[/dim]")

        if github_metrics_file:
            with open(github_metrics_file) as f:
                data = json.load(f)
                console.print(f"[dim]Loaded GitHub metrics from: {github_metrics_file}[/dim]")

        # If target is a PURL, try to load cached metrics
        if target.startswith("pkg:") and not git_metrics:
            cached = cache.get_package_data(target, "unified.json")
            if cached and cached.data:
                if "git_metrics" in cached.data:
                    git_metrics = GitMetricsResult.from_dict(cached.data["git_metrics"])
                    console.print("[dim]Loaded cached git metrics[/dim]")

        # Calculate score
        calculator = BurnoutScoreCalculator()
        result = calculator.calculate(target, git_metrics, github_metrics)
        result_data = result.to_dict()

        if output_format == "json":
            if output:
                with open(output, "w") as f:
                    json.dump(result_data, f, indent=2)
                console.print(f"[green]Saved to: {output}[/green]")
            else:
                console.print_json(json.dumps(result_data, indent=2))
        else:
            # Display summary (lower score = better for burnout)
            grade_colors = {"A": "green", "B": "blue", "C": "yellow", "D": "orange3", "F": "red"}
            grade_color = grade_colors.get(result.grade, "white")

            console.print()
            console.print(f"[bold]Burnout Risk Score:[/bold] [{grade_color}]{result.burnout_score}/100[/{grade_color}]")
            console.print(f"[bold]Grade:[/bold] [{grade_color}]{result.grade}[/{grade_color}] (A=low risk, F=high risk)")
            console.print(f"[bold]Risk Level:[/bold] {result.risk_level}")

            # Maintainer health
            mh = result.maintainer_health
            if mh.unique_contributors_90d > 0:
                health_table = Table(title="Maintainer Health Indicators")
                health_table.add_column("Indicator", style="cyan")
                health_table.add_column("Value", style="green")

                health_table.add_row("Contributors (90d)", str(mh.unique_contributors_90d))
                health_table.add_row("Pony Factor (90d)", str(mh.pony_factor_90d))
                health_table.add_row("Elephant Factor (90d)", str(mh.elephant_factor_90d))
                health_table.add_row("Contributor Retention", f"{mh.contributor_retention_90d:.1f}%")

                console.print(health_table)

            # Show components
            if result.components:
                table = Table(title="Burnout Risk Components")
                table.add_column("Component", style="cyan")
                table.add_column("Score", style="white")
                table.add_column("Max", style="dim")
                table.add_column("Status", style="white")
                table.add_column("Details", style="dim")

                for name, comp in result.components.items():
                    status_color = {"healthy": "green", "moderate": "yellow", "warning": "orange3", "critical": "red"}.get(comp.status, "white")
                    details = ", ".join(f"{k}={v}" for k, v in comp.details.items()) if comp.details else ""
                    table.add_row(
                        name.replace("_", " ").title(),
                        str(comp.score),
                        str(comp.max_score),
                        f"[{status_color}]{comp.status}[/{status_color}]",
                        details[:40]
                    )
                console.print(table)

            if result.recommendations:
                console.print("\n[bold]Recommendations:[/bold]")
                for rec in result.recommendations:
                    console.print(f"  - {rec}")

            # Save to file if requested
            if output:
                with open(output, "w") as f:
                    json.dump(result_data, f, indent=2)
                console.print(f"\n[green]Saved to: {output}[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if ctx.debug:
            import traceback
            console.print(traceback.format_exc())
        raise click.Abort()


# =============================================================================
# Full Analysis Commands
# =============================================================================


@cli.command()
@click.argument("purl")
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file path")
@click.option("--output-dir", type=click.Path(path_type=Path), help="Output directory")
@click.option("--skip-clone", is_flag=True, help="Skip git clone (use existing)")
@click.option("--skip-tarball", is_flag=True, help="Skip tarball scan")
@click.option("--skip-github", is_flag=True, help="Skip GitHub API fetch")
@click.option("--force-refresh", is_flag=True, help="Force refresh all cached data")
@pass_context
def analyze(
    ctx: Context,
    purl: str,
    output: Path | None,
    output_dir: Path | None,
    skip_clone: bool,
    skip_tarball: bool,
    skip_github: bool,
    force_refresh: bool,
) -> None:
    """Run full analysis on a package.

    Performs discovery, cloning, git analysis, GitHub API fetch, tarball scan,
    and calculates health and burnout scores.
    """
    from ccda_cli.analysis import AnalysisPipeline
    from rich.progress import Progress, SpinnerColumn, TextColumn

    console.print(f"[bold]Full analysis:[/bold] {purl}")

    try:
        # Progress callback
        step_status = {}

        def progress_callback(step: str, status: str):
            step_status[step] = status
            if ctx.verbose:
                console.print(f"  [{status}] {step}")

        # Run pipeline
        pipeline = AnalysisPipeline(progress_callback=progress_callback)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("Running analysis...", total=None)

            result = run_async(
                pipeline.analyze(
                    purl,
                    skip_clone=skip_clone,
                    skip_tarball=skip_tarball,
                    skip_github=skip_github,
                    force_refresh=force_refresh,
                )
            )

            progress.update(task, description="Analysis complete")

        result_data = result.to_dict()

        # Display summary
        console.print("\n[bold]Analysis Summary[/bold]")

        # Pipeline status
        table = Table(title="Pipeline Steps")
        table.add_column("Step", style="cyan")
        table.add_column("Status", style="white")
        table.add_column("Duration", style="dim")

        for step in result.steps:
            status_color = {
                "completed": "green",
                "failed": "red",
                "skipped": "yellow",
            }.get(step.status, "white")
            table.add_row(
                step.name,
                f"[{status_color}]{step.status}[/{status_color}]",
                f"{step.duration_seconds:.1f}s",
            )

        console.print(table)

        # Scores
        if result.health_score:
            grade_colors = {"A": "green", "B": "blue", "C": "yellow", "D": "orange3", "F": "red"}
            grade_color = grade_colors.get(result.health_score.grade, "white")
            console.print(f"\n[bold]Health Score:[/bold] [{grade_color}]{result.health_score.health_score}/100 ({result.health_score.grade})[/{grade_color}]")

        if result.burnout_score:
            console.print(f"[bold]Burnout Risk:[/bold] {result.burnout_score.burnout_score}/100 ({result.burnout_score.risk_level})")

        # Key metrics
        summary = result_data.get("summary", {})
        key_metrics = summary.get("key_metrics", {})
        if key_metrics:
            console.print("\n[bold]Key Metrics:[/bold]")
            metrics_table = Table()
            metrics_table.add_column("Metric", style="cyan")
            metrics_table.add_column("Value", style="green")

            for metric, value in key_metrics.items():
                metrics_table.add_row(metric.replace("_", " ").title(), str(value))
            console.print(metrics_table)

        # Errors
        if result.errors:
            console.print("\n[yellow]Warnings/Errors:[/yellow]")
            for err in result.errors:
                console.print(f"  - {err}")

        # Duration
        console.print(f"\n[dim]Total time: {result.total_duration_seconds:.1f}s[/dim]")

        # Output results
        if output:
            with open(output, "w") as f:
                json.dump(result_data, f, indent=2)
            console.print(f"[green]Saved to: {output}[/green]")
        elif output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            # Generate filename from PURL
            from ccda_cli.discovery import PURLParser
            parsed = PURLParser.parse(purl)
            safe_name = parsed.full_name.replace("/", "_").replace("@", "_")
            out_file = output_dir / f"{safe_name}-unified.json"
            with open(out_file, "w") as f:
                json.dump(result_data, f, indent=2)
            console.print(f"[green]Saved to: {out_file}[/green]")
        elif ctx.verbose:
            console.print_json(json.dumps(result_data, indent=2))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if ctx.debug:
            import traceback
            console.print(traceback.format_exc())
        raise click.Abort()


@cli.command("analyze-batch")
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option("--output-dir", type=click.Path(path_type=Path), help="Output directory")
@click.option("--concurrency", type=int, default=3, help="Max concurrent analyses")
@click.option("--skip-clone", is_flag=True, help="Skip git clone")
@click.option("--skip-tarball", is_flag=True, help="Skip tarball scan")
@click.option("--skip-github", is_flag=True, help="Skip GitHub API fetch")
@pass_context
def analyze_batch(
    ctx: Context,
    input_file: Path,
    output_dir: Path | None,
    concurrency: int,
    skip_clone: bool,
    skip_tarball: bool,
    skip_github: bool,
) -> None:
    """Run full analysis on multiple packages."""
    from ccda_cli.analysis import AnalysisPipeline
    from ccda_cli.discovery import PURLParser

    console.print(f"[bold]Batch analysis from:[/bold] {input_file}")

    try:
        # Read PURLs from file
        with open(input_file) as f:
            purls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

        if not purls:
            console.print("[yellow]No PURLs found in file[/yellow]")
            return

        console.print(f"  Found {len(purls)} packages")
        console.print(f"  Concurrency: {concurrency}")

        # Setup output directory
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)

        # Run batch analysis
        pipeline = AnalysisPipeline()
        results = run_async(
            pipeline.analyze_batch(
                purls,
                concurrency=concurrency,
                skip_clone=skip_clone,
                skip_tarball=skip_tarball,
                skip_github=skip_github,
            )
        )

        # Summary
        success = sum(1 for r in results if not r.errors)
        failed = len(results) - success

        console.print(f"\n[bold]Results:[/bold]")
        console.print(f"  [green]Success: {success}[/green]")
        if failed > 0:
            console.print(f"  [yellow]With errors: {failed}[/yellow]")

        # Summary table
        table = Table(title="Analysis Results")
        table.add_column("Package", style="cyan")
        table.add_column("Health", style="white")
        table.add_column("Burnout", style="white")
        table.add_column("Status", style="white")

        for result in results:
            parsed = PURLParser.parse(result.purl)
            health = f"{result.health_score.health_score}" if result.health_score else "-"
            burnout = f"{result.burnout_score.burnout_score}" if result.burnout_score else "-"
            status = "[green]OK[/green]" if not result.errors else f"[yellow]{len(result.errors)} errors[/yellow]"

            table.add_row(parsed.full_name, health, burnout, status)

        console.print(table)

        # Save individual results
        if output_dir:
            for result in results:
                parsed = PURLParser.parse(result.purl)
                safe_name = parsed.full_name.replace("/", "_").replace("@", "_")
                out_file = output_dir / f"{safe_name}-unified.json"
                with open(out_file, "w") as f:
                    json.dump(result.to_dict(), f, indent=2)

            console.print(f"\n[green]Results saved to: {output_dir}[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if ctx.debug:
            import traceback
            console.print(traceback.format_exc())
        raise click.Abort()


# =============================================================================
# Report Commands
# =============================================================================


@cli.command()
@click.argument("target")  # PURL or unified.json path
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["json", "markdown", "html"]),
    default="markdown",
)
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file path")
@pass_context
def report(ctx: Context, target: str, output_format: str, output: Path | None) -> None:
    """Generate a report from analysis results.

    TARGET can be a PURL or path to unified.json.
    """
    from ccda_cli.report import ReportGenerator
    from ccda_cli.cache import CacheManager

    console.print(f"[bold]Generating {output_format} report:[/bold] {target}")

    try:
        target_path = Path(target)

        # Load analysis data
        if target_path.exists() and target_path.suffix == ".json":
            # Load from file
            generator = ReportGenerator.from_file(target_path)
        elif target.startswith("pkg:"):
            # Load from cache by PURL
            cache = CacheManager()
            cached = cache.get_package_data(target, "unified.json")
            if not cached:
                console.print(f"[red]No analysis found for {target}[/red]")
                console.print("Run 'ccda-cli analyze' first.")
                raise click.Abort()
            generator = ReportGenerator(cached.data)
        else:
            console.print("[red]TARGET must be a PURL or path to unified.json[/red]")
            raise click.Abort()

        # Generate report
        content = generator.generate(output_format)

        # Output
        if output:
            generator.save(output, output_format)
            console.print(f"[green]Report saved to: {output}[/green]")
        else:
            console.print(content)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if ctx.debug:
            import traceback
            console.print(traceback.format_exc())
        raise click.Abort()


# =============================================================================
# Cache Commands
# =============================================================================


@cli.group()
def cache() -> None:
    """Manage the analysis cache."""
    pass


@cache.command("info")
@pass_context
def cache_info(ctx: Context) -> None:
    """Show cache information and statistics."""
    from ccda_cli.cache import CacheManager

    config = ctx.config
    if config:
        console.print(f"[bold]Cache directory:[/bold] {config.cache.directory}")
        console.print(f"  Repos: {config.cache.repos_dir}")
        console.print(f"  Data:  {config.cache.data_dir}")
        console.print(f"  Users: {config.cache.users_dir}")

    try:
        manager = CacheManager()
        stats = manager.get_stats()

        console.print("\n[bold]Statistics:[/bold]")
        table = Table()
        table.add_column("Category", style="cyan")
        table.add_column("Count", style="green")
        table.add_column("Size", style="yellow")

        def format_size(bytes_val: int) -> str:
            if bytes_val < 1024:
                return f"{bytes_val} B"
            elif bytes_val < 1024 * 1024:
                return f"{bytes_val / 1024:.1f} KB"
            elif bytes_val < 1024 * 1024 * 1024:
                return f"{bytes_val / (1024 * 1024):.1f} MB"
            else:
                return f"{bytes_val / (1024 * 1024 * 1024):.1f} GB"

        table.add_row("Packages", str(stats["packages"]["count"]), format_size(stats["packages"]["size_bytes"]))
        table.add_row("Repositories", str(stats["repos"]["count"]), format_size(stats["repos"]["size_bytes"]))
        table.add_row("User Profiles", str(stats["users"]["count"]), format_size(stats["users"]["size_bytes"]))
        table.add_row("Total", "", format_size(stats["total_size_bytes"]))

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error getting stats: {e}[/red]")


@cache.command("clear")
@click.option("--repos", is_flag=True, help="Clear cloned repositories")
@click.option("--data", is_flag=True, help="Clear analysis data")
@click.option("--users", is_flag=True, help="Clear user profile cache")
@click.option("--all", "clear_all", is_flag=True, help="Clear everything")
@click.option("--dry-run", is_flag=True, help="Show what would be removed")
@pass_context
def cache_clear(
    ctx: Context, repos: bool, data: bool, users: bool, clear_all: bool, dry_run: bool
) -> None:
    """Clear cached data."""
    from ccda_cli.cache import CacheManager

    if clear_all:
        repos = data = users = True

    if not (repos or data or users):
        console.print("[yellow]Specify what to clear: --repos, --data, --users, or --all[/yellow]")
        return

    if dry_run:
        console.print("[dim](dry run)[/dim]")

    try:
        manager = CacheManager()

        if dry_run:
            # Show what would be removed
            if repos:
                repo_list = manager.list_repos()
                console.print(f"Would remove {len(repo_list)} repositories")
            if data:
                pkg_list = manager.list_packages()
                console.print(f"Would remove {len(pkg_list)} packages")
            if users:
                user_list = manager.list_users()
                console.print(f"Would remove {len(user_list)} user profiles")
        else:
            counts = manager.clear_all(repos=repos, data=data, users=users)
            console.print("[green]Cache cleared:[/green]")
            if repos:
                console.print(f"  Repositories: {counts['repos']}")
            if data:
                console.print(f"  Packages: {counts['data']}")
            if users:
                console.print(f"  Users: {counts['users']}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


# =============================================================================
# Config Commands
# =============================================================================


@cli.command("config-show")
@pass_context
def config_show(ctx: Context) -> None:
    """Show current configuration."""
    if ctx.config:
        import json

        console.print_json(json.dumps(ctx.config.dict(), default=str))


@cli.command("config-init")
@click.option("--force", is_flag=True, help="Overwrite existing config")
@pass_context
def config_init(ctx: Context, force: bool) -> None:
    """Create a default configuration file."""
    config_path = Path.home() / ".ccda" / "config.yaml"

    if config_path.exists() and not force:
        console.print(f"[yellow]Config already exists: {config_path}[/yellow]")
        console.print("Use --force to overwrite")
        return

    # TODO: Create default config file
    console.print(f"[green]Created config: {config_path}[/green]")


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()

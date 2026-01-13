import argparse
import sys
import time
from argparse import Namespace, _SubParsersAction
from pathlib import Path
from rich.console import Console
from rich.table import Table
from ..core import find_projects, sort_projects_by_dependency
from ..install import install_project

def register(subparsers: _SubParsersAction, base_parser: argparse.ArgumentParser):
    """Register the install command."""
    install_parser = subparsers.add_parser("install", help="Install projects into the current environment", parents=[base_parser])
    install_parser.add_argument("project_name", help="Name of the project to install or 'all'")
    install_parser.add_argument("--no-editable", action="store_true", help="Install in standard mode instead of editable")
    install_parser.set_defaults(func=execute)

def execute(args: Namespace, console: Console):
    """Execute the install command."""
    root_path = Path(args.path).resolve()
    all_projects = find_projects(
        root_path,
        recursive=getattr(args, "recursive", False),
        max_depth=getattr(args, "depth", 2),
        include_root=getattr(args, "include_root", None)
    )
    target_projects = []

    if args.project_name == "all":
        try:
            target_projects = sort_projects_by_dependency(all_projects)
            if getattr(args, "from_root", False):
                target_projects = [p for p in target_projects if p.path.resolve() != root_path.resolve()]
        except ValueError as e:
            console.print(f"[red]Dependency sorting failed: {e}[/red]")
            sys.exit(1)
    else:
        # 1. Try path-based matching (e.g. relm install packages/my-lib)
        input_path = Path(args.project_name)
        if not input_path.is_absolute():
            target_dir = (root_path / input_path).resolve()
        else:
            target_dir = input_path.resolve()

        if target_dir.exists() and target_dir.is_dir():
            # Filter all projects that are under this directory or IS this directory
            target_projects = [
                p for p in all_projects 
                if p.path.resolve() == target_dir or target_dir in p.path.resolve().parents
            ]
            if target_projects:
                try:
                    target_projects = sort_projects_by_dependency(target_projects)
                except ValueError as e:
                    console.print(f"[red]Dependency sorting failed: {e}[/red]")
                    sys.exit(1)
                
                if len(target_projects) > 1:
                    console.print(f"[bold]Targeting {len(target_projects)} projects in: [cyan]{args.project_name}[/cyan][/bold]")
        
        # 2. If no projects found via path, try exact name match
        if not target_projects:
            target = next((p for p in all_projects if p.name == args.project_name), None)
            if not target:
                console.print(f"[red]Project or folder '{args.project_name}' not found in {root_path}[/red]")
                sys.exit(1)
            target_projects = [target]

    results = {"installed": [], "failed": []}
    editable_mode = not args.no_editable

    if getattr(args, "parallel", False):
        from ..runner import execute_in_parallel
        
        def cmd_provider(p):
            # We need to construct the pip install command manually for parallel runner
            # since install_project uses subprocess directly.
            mode = "-e" if editable_mode else ""
            return [sys.executable, "-m", "pip", "install", mode, "."]

        results_data = execute_in_parallel(
            target_projects,
            command_provider=cmd_provider,
            max_workers=args.jobs,
            fail_fast=True, # Always fail-fast for installation dependencies
            cwd=None # CRITICAL: Always run pip install inside the project directory
        )
        
        for res in results_data:
            if res["success"]:
                results["installed"].append({"name": res["name"], "duration": res.get("duration", 0)})
            else:
                results["failed"].append({"name": res["name"], "duration": res.get("duration", 0)})
                console.rule(f"[red]Output for FAILED project: {res['name']}[/red]")
                from rich.markup import escape
                if res["stdout"]: console.print(escape(res["stdout"]))
                if res["stderr"]: console.print(escape(res["stderr"]), style="red")
    else:
        start_time_all = time.time()
        for project in target_projects:
            task_start = time.time()
            success = install_project(project, editable=editable_mode)
            task_duration = time.time() - task_start
            if success:
                results["installed"].append({"name": project.name, "duration": task_duration})
            else:
                results["failed"].append({"name": project.name, "duration": task_duration})
        total_duration = time.time() - start_time_all

    if args.project_name == "all":
        console.rule("Bulk Install Summary")
        
        table = Table(show_header=True, header_style="bold")
        table.add_column("Project", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Duration", justify="right")

        for item in results["installed"]:
            table.add_row(item["name"], "[green]Installed[/green]", f"{item['duration']:.2f}s")
        for item in results["failed"]:
            table.add_row(item["name"], "[red]Failed[/red]", f"{item['duration']:.2f}s")
        
        console.print(table)
        
        # We need total_duration. In parallel mode it's in results_data[0]['total_duration']
        actual_total = total_duration if not getattr(args, "parallel", False) else results_data[0].get("total_duration", 0)

        console.print(f"[bold]Completed bulk install in {actual_total:.2f}s.[/bold]")
        console.print(f"[green]Installed: {len(results['installed'])}[/green]")
        if results["failed"]:
            console.print(f"[red]Failed:    {len(results['failed'])}[/red]")

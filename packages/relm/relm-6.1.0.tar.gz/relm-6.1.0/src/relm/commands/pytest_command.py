import argparse
import sys
import subprocess
import time
from argparse import Namespace, _SubParsersAction
from pathlib import Path
from rich.console import Console
from rich.table import Table
from ..core import find_projects, sort_projects_by_dependency
from ..runner import execute_in_parallel

def register(subparsers: _SubParsersAction, base_parser: argparse.ArgumentParser):
    """Register the pytest command."""
    pytest_parser = subparsers.add_parser("pytest", help="Run pytest across projects and summarize results", parents=[base_parser])
    pytest_parser.add_argument(
        "project_name", 
        nargs="?", 
        default="all", 
        help="Name of the project to run on or 'all' (default: all)"
    )
    pytest_parser.add_argument(
        "--fail-fast", 
        action="store_true", 
        help="Stop execution if a project's tests fail"
    )
    # We default from_root to True for pytest as it is the standard monorepo workflow
    pytest_parser.set_defaults(func=execute, from_root=True)

def execute(args: Namespace, console: Console):
    """Execute the pytest command."""
    # Manual extraction of pytest arguments from sys.argv
    pytest_args = []
    if "--" in sys.argv:
        idx = sys.argv.index("--")
        pytest_args = sys.argv[idx + 1:]

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
            # If running from root and we have multiple projects, skip the project that IS the root 
            # to avoid double execution (since running pytest from root usually finds sub-tests anyway)
            if getattr(args, "from_root", False) and len(target_projects) > 1:
                target_projects = [p for p in target_projects if p.path.resolve() != root_path.resolve()]
        except ValueError as e:
            console.print(f"[red]Dependency sorting failed: {e}[/red]")
            sys.exit(1)
    else:
        # 1. Try path-based matching (e.g. relm pytest packages/my-lib)
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
                
                # Only print targeting info if it's actually a multi-project folder or different from name
                if len(target_projects) > 1:
                    console.print(f"[bold]Targeting {len(target_projects)} projects in: [cyan]{args.project_name}[/cyan][/bold]")
        
        # 2. If no projects found via path, try exact name match
        if not target_projects:
            target = next((p for p in all_projects if p.name == args.project_name), None)
            if not target:
                console.print(f"[red]Project or folder '{args.project_name}' not found in {root_path}[/red]")
                sys.exit(1)
            target_projects = [target]

    console.print(f"[bold]Running pytest on {len(target_projects)} projects...[/bold]")
    if pytest_args:
        console.print(f"[dim]Pytest arguments: {' '.join(pytest_args)}[/dim]")

    use_from_root = getattr(args, "from_root", False)
    cwd = root_path if use_from_root else None

    if getattr(args, "parallel", False):
        def cmd_provider(p):
            base_cmd = [sys.executable, "-m", "pytest"]
            
            # Create a unique directory for this project's coverage data.
            # This ensures that 'pytest-cov' combine/report operations are perfectly isolated
            # and won't attempt to access data from other projects.
            cov_dir = root_path / ".relm_cov" / p.name
            cov_dir.mkdir(parents=True, exist_ok=True)
            cov_data_path = cov_dir / ".coverage"

            if use_from_root:
                try:
                    target_path = str(p.path.relative_to(root_path))
                except ValueError:
                    target_path = str(p.path)
                cmd = base_cmd + [target_path]
            else:
                cmd = base_cmd
            
            cmd = cmd + pytest_args
            
            # Setting COVERAGE_FILE to an absolute path in a unique directory 
            # provides the highest level of isolation for pytest-cov.
            env = {
                "COVERAGE_FILE": str(cov_data_path.resolve()),
            }
            return cmd, env

        results_data = execute_in_parallel(
            target_projects,
            command_provider=cmd_provider,
            max_workers=args.jobs,
            fail_fast=args.fail_fast,
            cwd=cwd
        )
        # Map back to simple results format for summary
        results = results_data
        
        # Cleanup temporary coverage directories
        import shutil
        try:
            shutil.rmtree(root_path / ".relm_cov", ignore_errors=True)
        except Exception:
            pass

        # In parallel mode, show output for failed projects since it was captured
        for res in results:
            if not res["success"]:
                console.rule(f"[red]Summary for FAILED project: {res['name']}[/red]")
                if res["stdout"]:
                    from rich.panel import Panel
                    from rich.markup import escape
                    console.print(Panel(
                        escape(res["stdout"]), 
                        title="Last 50 lines of output", 
                        subtitle="Truncated to prevent system crash",
                        border_style="red"
                    ))
                if res["stderr"]:
                    from rich.markup import escape
                    console.print(escape(res["stderr"]), style="red")
    else:
        results = []
        start_time_all = time.time()
        for project in target_projects:
            console.rule(f"Testing {project.name}")
            
            base_cmd = [sys.executable, "-m", "pytest"]
            if use_from_root:
                try:
                    target_path = str(project.path.relative_to(root_path))
                except ValueError:
                    target_path = str(project.path)
                cmd = base_cmd + [target_path] + pytest_args
            else:
                cmd = base_cmd + pytest_args
            
            try:
                from ..runner import run_project_command_tail
                task_start = time.time()
                res_data = run_project_command_tail(cwd or project.path, cmd, tail_lines=50)
                task_duration = time.time() - task_start
                success = (res_data["returncode"] == 0)
                
                if not success:
                    from rich.panel import Panel
                    from rich.markup import escape
                    console.print(Panel(
                        escape(res_data["stdout"]), 
                        title=f"Failure Summary: {project.name}", 
                        subtitle="Last 50 lines of output",
                        border_style="red"
                    ))
            except Exception as e:
                console.print(f"[red]Error executing pytest in {project.name}: {e}[/red]")
                success = False
                res_data = {"stdout": str(e), "stderr": ""}
                task_duration = 0

            results.append({
                "name": project.name,
                "success": success,
                "path": project.path,
                "stdout": res_data["stdout"],
                "duration": task_duration
            })

            if not success and args.fail_fast:
                console.print(f"[red]Fail-fast enabled. Stopping further tests.[/red]")
                break
        
        total_duration = time.time() - start_time_all
        for res in results:
            res["total_duration"] = total_duration

    # Final Summary
    console.rule("Pytest Summary")
    
    # Cleanup temporary coverage files
    import shutil
    relm_cov_dir = root_path / ".relm_cov"
    if relm_cov_dir.exists():
        try:
            shutil.rmtree(relm_cov_dir)
        except Exception:
            pass

    table = Table(show_header=True, header_style="bold")
    table.add_column("Project", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Duration", justify="right")
    table.add_column("Path", style="dim")

    passed_count = 0
    total_time = 0
    for res in results:
        status = "[green]PASSED[/green]" if res["success"] else "[red]FAILED[/red]"
        if res["success"]:
            passed_count += 1
        
        duration = res.get("duration", 0)
        table.add_row(res["name"], status, f"{duration:.2f}s", str(res["path"]))
        total_time = res.get("total_duration", 0)

    console.print(table)

    total = len(target_projects)
    run_count = len(results)
    failed_count = run_count - passed_count

    summary_msg = f"[bold]Ran tests for {run_count}/{total} projects in {total_time:.2f}s.[/bold] "
    summary_msg += f"[green]{passed_count} passed[/green], [red]{failed_count} failed[/red]."
    
    if run_count < total:
        summary_msg += f" [yellow]({total - run_count} skipped due to fail-fast)[/yellow]"
    
    console.print(summary_msg)

    if failed_count > 0:
        sys.exit(1)

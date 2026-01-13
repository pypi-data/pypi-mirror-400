import pytest
from pathlib import Path
from argparse import Namespace
from rich.console import Console
from relm.commands import pytest_command, run_command, install_command, status_command
from relm.core import Project

@pytest.fixture
def mock_projects(tmp_path):
    # Create a structure:
    # packages/
    #   lib1/pyproject.toml
    #   lib2/pyproject.toml
    # services/
    #   bot1/pyproject.toml
    
    pkg_dir = tmp_path / "packages"
    svc_dir = tmp_path / "services"
    pkg_dir.mkdir()
    svc_dir.mkdir()
    
    lib1_path = pkg_dir / "lib1"
    lib1_path.mkdir()
    (lib1_path / "pyproject.toml").write_text('[project]\nname="lib1"\nversion="1.0.0"')
    
    lib2_path = pkg_dir / "lib2"
    lib2_path.mkdir()
    (lib2_path / "pyproject.toml").write_text('[project]\nname="lib2"\nversion="1.0.0"')
    
    bot1_path = svc_dir / "bot1"
    bot1_path.mkdir()
    (bot1_path / "pyproject.toml").write_text('[project]\nname="bot1"\nversion="1.0.0"')
    
    return [
        Project(name="lib1", version="1.0.0", path=lib1_path),
        Project(name="lib2", version="1.0.0", path=lib2_path),
        Project(name="bot1", version="1.0.0", path=bot1_path),
    ]

def test_path_targeting_pytest(mock_projects, tmp_path, mocker):
    mocker.patch("relm.commands.pytest_command.find_projects", return_value=mock_projects)
    mock_exec = mocker.patch("relm.commands.pytest_command.execute_in_parallel", return_value=[])
    console = Console()
    
    # Test targeting a subdirectory path
    args = Namespace(
        path=str(tmp_path),
        project_name="packages",
        recursive=True,
        depth=2,
        parallel=True,
        jobs=None,
        from_root=False,
        fail_fast=False
    )
    
    pytest_command.execute(args, console)
    
    # Should have targeted lib1 and lib2
    target_projects = mock_exec.call_args[0][0]
    names = {p.name for p in target_projects}
    assert names == {"lib1", "lib2"}
    assert "bot1" not in names

def test_path_targeting_run(mock_projects, tmp_path, mocker):
    mocker.patch("relm.commands.run_command.find_projects", return_value=mock_projects)
    mock_run = mocker.patch("relm.commands.run_command.run_project_command", return_value=True)
    console = Console()
    
    # Test targeting specific project path
    args = Namespace(
        path=str(tmp_path),
        project_name="services/bot1",
        command_string="echo hello",
        recursive=True,
        depth=2,
        parallel=False,
        from_root=False,
        fail_fast=False
    )
    
    run_command.execute(args, console)
    
    # Should have called run_project_command once for bot1
    assert mock_run.call_count == 1
    assert "bot1" in str(mock_run.call_args[0][0])

def test_path_targeting_install(mock_projects, tmp_path, mocker):
    mocker.patch("relm.commands.install_command.find_projects", return_value=mock_projects)
    mock_run = mocker.patch("relm.commands.install_command.install_project", return_value=True)
    console = Console()
    
    args = Namespace(
        path=str(tmp_path),
        project_name="packages/lib1",
        no_editable=False,
        recursive=True,
        depth=2,
        parallel=False,
        from_root=False
    )
    
    install_command.execute(args, console)
    assert mock_run.call_count == 1
    # Check that the first argument to install_project was the correct project object
    assert mock_run.call_args[0][0].name == "lib1"

def test_path_targeting_status(mock_projects, tmp_path, mocker):
    mocker.patch("relm.commands.status_command.find_projects", return_value=mock_projects)
    mocker.patch("relm.commands.status_command.get_current_branch", return_value="main")
    mocker.patch("relm.commands.status_command.is_git_clean", return_value=True)
    
    spy_table = mocker.spy(Console, "print")
    console = Console()
    
    args = Namespace(
        path=str(tmp_path),
        project_name="packages",
        recursive=True,
        depth=2
    )
    
    status_command.execute(args, console)
    # Verify that it targetted 2 projects (lib1, lib2)
    # The title of the table contains the count
    table = spy_table.call_args[0][1]
    assert "2 Projects" in table.title

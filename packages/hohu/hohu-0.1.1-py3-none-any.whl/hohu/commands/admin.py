import shutil
import subprocess
from pathlib import Path

import questionary
import typer
from rich.console import Console

from hohu.i18n import i18n
from hohu.utils.project import ProjectManager

console = Console()
admin_app = typer.Typer(help="Admin commands for projects")

REPOS = {
    "Backend": "https://github.com/aihohu/hohu-admin.git",
    "Frontend": "https://github.com/aihohu/hohu-admin-web.git",
    "App": "https://github.com/aihohu/hohu-admin-app.git",
}


@admin_app.command()
def create(project_name: str = typer.Argument("hohu-admin")):
    """Create a new project directory and clone templates"""
    root = Path.cwd() / project_name
    if root.exists():
        console.print(f"[red]Error: {project_name} already exists.[/red]")
        return

    choices = questionary.checkbox(
        i18n.t("select_components"),
        choices=[
            questionary.Choice("Backend", checked=True),
            questionary.Choice("Frontend", checked=True),
            questionary.Choice("App", checked=True),
        ],
    ).ask()

    if not choices:
        return

    try:
        root.mkdir(parents=True)
        ProjectManager.mark_project(root, project_name, choices)

        for item in choices:
            folder = {
                "Backend": "hohu-admin",
                "Frontend": "hohu-admin-web",
                "App": "hohu-admin-app",
            }[item]
            console.print(f"🚚 [blue]{i18n.t('cloning')} {item}...[/blue]")
            subprocess.run(
                ["git", "clone", REPOS[item], str(root / folder)], check=True
            )

        console.print(
            f"\n✨ {i18n.t('success_msg')} [bold cyan]cd {project_name} && hohu admin init[/bold cyan]"
        )
    except Exception as e:
        console.print(f"[red]Failed: {e}[/red]")


@admin_app.command()
def init():
    """Initialize environment for the current project (uv/pnpm)"""
    root = ProjectManager.find_root()
    if not root:
        console.print(f"[red]{i18n.t('not_in_project')}[/red]")
        return

    info = ProjectManager.get_info(root)
    console.print(f"🛠️  [bold]Initializing: {info['name']}[/bold]\n")

    for item in info["components"]:
        folder = {
            "Backend": "hohu-admin",
            "Frontend": "hohu-admin-web",
            "App": "hohu-admin-app",
        }[item]
        path = root / folder

        if not path.exists():
            continue

        if item == "Backend":
            cmd = (
                ["uv", "sync"]
                if shutil.which("uv")
                else ["pip", "install", "-r", "requirements.txt"]
            )
        else:
            cmd = ["pnpm", "install"] if shutil.which("pnpm") else ["npm", "install"]

        console.print(f"📦 [dim]Executing {' '.join(cmd)} in {folder}...[/dim]")
        subprocess.run(cmd, cwd=path)

    console.print(f"\n✅ {i18n.t('init_success')}")

import subprocess

import questionary
import typer
from rich.console import Console

from hohu.utils.i18n import i18n

console = Console()
admin_app = typer.Typer(help="Management System Commands")

REPOS = {
    "Backend": "https://github.com/aihohu/hohu-admin.git",
    "Frontend": "https://github.com/aihohu/hohu-admin-web.git",
    "App": "https://github.com/aihohu/hohu-admin-app.git",
}


@admin_app.command()
def create(
    project_name: str | None = typer.Argument(
        None, help="The name of the project. Defaults to 'hohu-admin'"
    ),
):
    """
    创建项目。默认名称为 hohu-admin。
    """
    # 如果用户没有提供 project_name，使用默认值
    if not project_name:
        project_name = "hohu-admin"

    try:
        # 1. 交互式选择组件
        choices = questionary.checkbox(
            i18n.t("select_components"),
            choices=[
                questionary.Choice(
                    "Backend (hohu-admin)", checked=True, value="Backend"
                ),
                questionary.Choice(
                    "Frontend (hohu-admin-web)", checked=True, value="Frontend"
                ),
                questionary.Choice("App (hohu-admin-app)", checked=True, value="App"),
            ],
        ).ask()

        # 如果用户直接按了 Ctrl+C 或者什么都没选
        if choices is None:
            raise KeyboardInterrupt

        if not choices:
            console.print(f"[yellow]⚠ {i18n.t('no_selection')}[/yellow]")
            return

        # 2. 依次克隆
        for item in choices:
            repo_url = REPOS[item]
            # 后端目录直接用 project_name，其他加后缀
            if item == "Backend":
                folder_name = project_name
            else:
                suffix = "web" if item == "Frontend" else "app"
                folder_name = f"{project_name}-{suffix}"

            console.print(f"🚀 [bold blue]{i18n.t('cloning')} {item}...[/bold blue]")

            # 使用 subprocess 执行 git clone
            result = subprocess.run(
                ["git", "clone", repo_url, folder_name], capture_output=True, text=True
            )

            if result.returncode != 0:
                console.print(f"[red]FAILED:[/red] {result.stderr}")
            else:
                console.print(f"[green]✓ {folder_name}[/green]")

        console.print(
            f"\n✨ [bold green]{i18n.t('success_msg')} {project_name}[/bold green]"
        )

    except KeyboardInterrupt:
        console.print(f"\n[red]✘ {i18n.t('aborted')}[/red]")
        raise typer.Exit()

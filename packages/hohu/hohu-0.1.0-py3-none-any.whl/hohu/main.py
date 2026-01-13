import questionary
import typer
from rich.console import Console

from hohu.commands import admin
from hohu.utils.i18n import i18n

console = Console()
app = typer.Typer(name="hohu", help="Hohu CLI Tool")

app.add_typer(admin.admin_app, name="admin")


@app.command()
def lang():
    """切换交互语言 / Switch interaction language."""
    new_lang = questionary.select(
        i18n.t("select_lang_prompt"),
        choices=[
            questionary.Choice("简体中文", value="zh"),
            questionary.Choice("English", value="en"),
        ],
    ).ask()

    if new_lang:
        i18n.set_lang(new_lang)
        console.print(
            f"[green]✔[/green] {i18n.t('lang_selected')} [bold]{new_lang}[/bold]"
        )


if __name__ == "__main__":
    app()

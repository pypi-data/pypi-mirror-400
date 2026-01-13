import questionary
import typer
from rich.console import Console

from hohu.config import load_config, save_config
from hohu.i18n import i18n

console = Console()
system_app = typer.Typer(help="System settings")


@system_app.command("lang")
def set_language():
    """设置 CLI 交互语言"""
    choices = [
        questionary.Choice("简体中文", value="zh"),
        questionary.Choice("English", value="en"),
        questionary.Choice("Follow System (跟随系统)", value="auto"),
    ]

    selected_lang = questionary.select(i18n.t("select_lang"), choices=choices).ask()

    if selected_lang:
        config = load_config()
        config["language"] = selected_lang
        save_config(config)

        # 刷新 i18n 实例以立即生效
        i18n.refresh()
        console.print(i18n.t("lang_updated"))

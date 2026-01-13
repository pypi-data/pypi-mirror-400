import json
from pathlib import Path

# 定义配置文件路径：~/.hohu/config.json
CONFIG_DIR = Path.home() / ".hohu"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "language": "auto"  # auto 表示跟随系统，也可以是 zh 或 en
}


def load_config():
    """从本地加载配置"""
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_CONFIG


def save_config(config: dict):
    """保存配置到本地"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


def get_lang():
    """获取当前设定的语言"""
    return load_config().get("language", "auto")

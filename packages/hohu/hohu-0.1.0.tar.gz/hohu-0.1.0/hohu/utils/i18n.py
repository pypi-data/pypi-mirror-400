import json
import locale
from pathlib import Path

# 默认配置路径
CONFIG_FILE = Path.home() / ".hohu_config.json"


class I18n:
    def __init__(self):
        self.lang = self._load_config()
        self.locales = self._load_locales()

    def _load_config(self):
        if CONFIG_FILE.exists():
            config = json.loads(CONFIG_FILE.read_text())
            return config.get("lang", self._get_system_lang())
        return self._get_system_lang()

    def _get_system_lang(self):
        default = locale.getdefaultlocale()[0]
        return "zh" if default and "zh" in default else "en"

    def _load_locales(self):
        locales_dir = Path(__file__).parent.parent / "locales"
        data = {}
        for f in locales_dir.glob("*.json"):
            data[f.stem] = json.loads(f.read_text(encoding="utf-8"))
        return data

    def t(self, key):
        return self.locales.get(self.lang, self.locales["en"]).get(key, key)

    def set_lang(self, lang):
        self.lang = lang
        CONFIG_FILE.write_text(json.dumps({"lang": lang}))


i18n = I18n()

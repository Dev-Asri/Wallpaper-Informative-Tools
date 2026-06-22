import json
import os


class ConfigManager:
    """Manages wallpaper info tool settings (JSON)."""

    DEFAULTS = {
        "background_type": "color",
        "background_color": "#1e1e2e",
        "background_image": "",
        "items": [],
        "overlay_enabled": False,
        "update_interval": 10,
        "data_sources": ["network", "hardware", "system"],
        "startup_refresh": True,
        "preview_duration": 5,
        "row_spacing": 35,
        "startup_run_enabled": False,
        "startup_run_duration": 3,
        "lang": "tr",
    }

    def __init__(self, config_path=None):
        self.config_path = config_path or os.path.join(
            os.environ.get("APPDATA", os.path.expanduser("~")),
            "WallpaperInformativeTool",
            "settings.json",
        )
        self._data = dict(self.DEFAULTS)
        self._ensure_dir()

    def _ensure_dir(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

    def load(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                for k, v in self.DEFAULTS.items():
                    self._data[k] = loaded.get(k, v)
                self._data["items"] = loaded.get("items", [])
                self._data["startup_refresh"] = loaded.get("startup_refresh", True)
        except (FileNotFoundError, json.JSONDecodeError):
            self._data = dict(self.DEFAULTS)
        return self._data

    def save(self, data=None):
        if data:
            self._data.update(data)
        self._ensure_dir()
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value

    @property
    def data(self):
        return self._data

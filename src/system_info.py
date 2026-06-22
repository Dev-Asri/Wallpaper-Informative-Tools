import sys
import os
import importlib
import importlib.util

if getattr(sys, 'frozen', False):
    _BASE = sys._MEIPASS
else:
    _BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SYSINFO_SRC = os.path.join(_BASE, "windows_sysinfo")
_COL_SRC = os.path.join(_SYSINFO_SRC, "collectors")
if os.path.isdir(_COL_SRC):
    if _SYSINFO_SRC not in sys.path:
        sys.path.insert(0, _SYSINFO_SRC)
else:
    _DEV_PATH = r"D:\AICodeProje\PC_On_Hazirlik\BILGISAYAR_BILGI_TOPLA\windows_sysinfo"
    _DEV_COL = os.path.join(_DEV_PATH, "collectors")
    if os.path.isdir(_DEV_COL):
        if os.path.dirname(_DEV_PATH) not in sys.path:
            sys.path.insert(0, os.path.dirname(_DEV_PATH))
        _SYSINFO_SRC = _DEV_PATH
        _COL_SRC = _DEV_COL

_DEBUG_LOG = os.path.join(os.environ.get("TEMP", os.path.expanduser("~")), "wallpaper_collect_error.log")

_collector_cache = {}

def clear_collector_cache():
    _collector_cache.clear()

def _get_collector(name):
    if name not in _collector_cache:
        cls_name = {"network": "NetworkCollector", "hardware": "HardwareCollector",
                    "system": "SystemCollector", "database": "DataCollector"}[name]
        spec = importlib.util.spec_from_file_location(
            f"windows_sysinfo.collectors.{name}",
            os.path.join(_COL_SRC, f"{name}.py"),
            submodule_search_locations=[]
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load collector {name}")
        mod = importlib.util.module_from_spec(spec)
        # emulate package parent to allow relative imports
        # the collector modules do not use relative imports, so this is safe
        spec.loader.exec_module(mod)
        _collector_cache[name] = getattr(mod, cls_name)()
    return _collector_cache[name]


ALL_SOURCES = ["network", "hardware", "system", "database"]

_info_cache = {}

def clear_info_cache():
    _info_cache.clear()

def _cached_collect(name):
    if name not in _info_cache:
        try:
            c = _get_collector(name)
            _info_cache[name] = c.collect()
        except Exception as e:
            import traceback
            _debug_path = _DEBUG_LOG
            with open(_debug_path, "a", encoding="utf-8") as _df:
                _df.write(f"[{name}] Exception: {e}\n")
                _df.write(traceback.format_exc() + "\n")
            _info_cache[name] = {"_error": str(e)}
    return _info_cache[name]

def get_selected_info(sources):
    data = {}
    for name in sources:
        if name in ALL_SOURCES:
            try:
                data[name] = _cached_collect(name)
            except Exception as e:
                data[name] = {"_error": str(e)}
    return data

def get_all_info():
    return get_selected_info(ALL_SOURCES)


def get_network_info():
    return _cached_collect("network")

def get_hardware_info():
    return _cached_collect("hardware")

def get_system_info():
    return _cached_collect("system")

def get_database_info():
    return _cached_collect("database")

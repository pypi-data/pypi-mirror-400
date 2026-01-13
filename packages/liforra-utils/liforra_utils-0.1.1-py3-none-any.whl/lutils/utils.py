import json
import os
import configparser
from typing import Any, Dict, List, Optional, Tuple
from random import choice

_logger: Optional[Any] = None
_log_file_path: Optional[str] = None
_log_level: str = "info"
_LOG_FORMAT: str = "[%(asctime)s] %(levelname)s: %(message)s"
_COLOR_RESET: str = "\033[0m"
_COLOR_MAP: Dict[str, str] = {
    "fatal": "\033[1;31m",
    "err": "\033[31m",
    "warn": "\033[33m",
    "info": "\033[36m",
    "debug": "\033[90m",
}
configName: str = "config"
configPath: str = "./"
author: str = "Liforra"
website: str = "https://liforra.de"

__all__ = ["config", "log", "set_log_file", "set_log_level", "author", "website"]

_UNSET: object = object()



# utils.py

class _Maybe:
    def __bool__(self):
        return choice((True, False))

Maybe = _Maybe()


def __getattr__(name):
    match name:
        case _:
            raise AttributeError(name)
def _purple() -> str:
    import codecs
    import importlib
    import io
    import re
    from contextlib import redirect_stdout

    with redirect_stdout(io.StringIO()):
        this = importlib.import_module("this")
    zen = codecs.decode(this.s, "rot_13")
    replacements = {
        "Beautiful": "Purple",
        "Explicit": "Purple",
        "Simple": "Purple",
        "Complex": "Indigo",
        "Complicated": "Magenta",
        "Flat": "Purple",
        "Sparse": "Purple",
        "Readability": "Purple",
        "Special": "Orange",
        "Errors": "Crimson",
        "ambiguity": "Purple",
        "obvious": "Purple",
        "hard": "Gray",
        "easy": "Purple",
        "Namespaces": "Violet",
    }

    pattern = r"\b(" + "|".join(re.escape(key) for key in replacements) + r")\b"
    return re.sub(pattern, lambda match: replacements[match.group(0)], zen)


class _Config:
    def set_path(self, path: str) -> None:
        global configPath
        configPath = path

    def set_name(self, name: str) -> None:
        global configName
        configName = name

    def get(
        self,
        key: str,
        default: Any = _UNSET,
        config_name: Optional[str] = None,
        config_path: Optional[str] = None,
    ) -> Any:
        config_path = config_path if config_path is not None else configPath
        config_name = config_name if config_name is not None else configName
        config_data = _load_config(config_name=config_name, config_path=config_path)
        if config_data is None:
            if default is _UNSET:
                return None
            target = _select_config_target(config_path, config_name)
            config_data = target["data"] if target["data"] is not None else {}
            _set_value(config_data, key, default, target["format"])
            _write_config(target["path"], target["format"], config_data)
            return default
        value = _get_value(config_data, key)
        if value is not None:
            return value
        if default is _UNSET:
            return None
        target = _select_config_target(config_path, config_name)
        config_data = target["data"] if target["data"] is not None else {}
        _set_value(config_data, key, default, target["format"])
        _write_config(target["path"], target["format"], config_data)
        return default

    def set(
        self,
        key: str,
        value: Any,
        config_name: Optional[str] = None,
        config_path: Optional[str] = None,
    ) -> None:
        config_path = config_path if config_path is not None else configPath
        config_name = config_name if config_name is not None else configName
        target = _select_config_target(config_path, config_name)
        config_data = target["data"] if target["data"] is not None else {}
        _set_value(config_data, key, value, target["format"])
        _write_config(target["path"], target["format"], config_data)

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)


config = _Config()


def _make_formatter(colorize: bool = False) -> Optional[Any]:
    if _logging is None:
        return None

    class _MillisFormatter(_logging.Formatter):
        def format(self, record: Any) -> str:
            message = super().format(record)
            if not colorize:
                return message
            color = _COLOR_MAP.get(record.levelname.lower())
            if not color:
                return message
            return f"{color}{message}{_COLOR_RESET}"

        def formatTime(self, record: Any, datefmt: Optional[str] = None) -> str:
            from datetime import datetime

            timestamp = datetime.fromtimestamp(record.created)
            formatted = timestamp.strftime(datefmt or "%d.%m.%y %H:%M:%S.%f")
            if "." in formatted:
                return formatted[:-3]
            return formatted

    return _MillisFormatter(fmt=_LOG_FORMAT, datefmt="%d.%m.%y %H:%M:%S.%f")

try:
    import coloredlogs as _coloredlogs
except Exception:
    _coloredlogs = None

try:
    import logging as _logging
except Exception:
    _logging = None

try:
    import tomllib as _toml
except Exception:
    try:
        import toml as _toml
    except Exception:
        _toml = None

try:
    import yaml as _yaml
except Exception:
    _yaml = None


def set_log_file(path: str) -> None:
    global _log_file_path
    _log_file_path = path
    _attach_file_handler_if_ready()


def set_log_level(level: str) -> None:
    global _log_level
    _log_level = _normalize_level(level)
    if _logging is None:
        return
    _ensure_logger(use_coloredlogs=_coloredlogs is not None)
    if _logger is not None:
        _logger.setLevel(_level_value(_log_level))


def log(level: str, message: str, file_path: Optional[str] = None) -> None:
    normalized_level = _normalize_level(level)
    target_file = file_path if file_path is not None else _log_file_path

    if _logging is not None:
        try:
            use_coloredlogs = _coloredlogs is not None
            _ensure_logger(use_coloredlogs=use_coloredlogs)
            _attach_file_handler_if_ready(target_file)
            _logger.setLevel(_level_value(_log_level))
            _logger.log(_level_value(normalized_level), message)
            if normalized_level == "fatal":
                raise Exception(message)
            return
        except Exception as exc:
            if normalized_level == "fatal" and isinstance(exc, Exception) and str(exc) == str(message):
                raise

    from datetime import datetime

    timestamp = datetime.now().strftime("%d.%m.%y %H:%M.%f")[:-3]
    line = f"[{timestamp}] {normalized_level.upper()}: {message}"
    if _level_value(normalized_level) >= _level_value(_log_level):
        color = _COLOR_MAP.get(normalized_level)
        if color:
            line = f"{color}{line}{_COLOR_RESET}"
        if target_file:
            try:
                with open(target_file, "a") as handle:
                    handle.write(line + "\n")
            except Exception:
                pass
        else:
            print(line)
    if normalized_level == "fatal":
        raise Exception(message)



def _normalize_level(level: Any) -> str:
    if not isinstance(level, str):
        return "info"
    normalized = level.strip().lower()
    if "fatal" in normalized:
        return "fatal"
    if "error" in normalized or "err" in normalized:
        return "err"
    if "warn" in normalized:
        return "warn"
    if "debug" in normalized:
        return "debug"
    if "info" in normalized:
        return "info"
    return "info"


def _level_value(level: str) -> int:
    mapping = {
        "fatal": 50,
        "err": 40,
        "warn": 30,
        "info": 20,
        "debug": 10,
    }
    return mapping.get(level, 20)


def _ensure_logger(use_coloredlogs: bool) -> None:
    global _logger
    if _logger is not None:
        return
    if _logging is None:
        return
    _logger = _logging.getLogger("app")
    _logging.addLevelName(50, "FATAL")
    _logging.addLevelName(40, "ERR")
    _logging.addLevelName(30, "WARN")
    _logging.addLevelName(20, "INFO")
    _logging.addLevelName(10, "DEBUG")
    if _logger.handlers:
        return
    if use_coloredlogs:
        if _coloredlogs is None:
            return
        _coloredlogs.install(level="INFO", logger=_logger)
        formatter = _make_formatter(colorize=True)
        for handler in _logger.handlers:
            if isinstance(handler, _logging.Handler):
                if formatter is not None:
                    handler.setFormatter(formatter)
    else:
        handler = _logging.StreamHandler()
        formatter = _make_formatter(colorize=True)
        if formatter is not None:
            handler.setFormatter(formatter)
        _logger.addHandler(handler)
    _logger.setLevel(_level_value(_log_level))


def _attach_file_handler_if_ready(path: Optional[str] = None) -> None:
    if _logger is None:
        return
    target_path = path if path is not None else _log_file_path
    if not target_path:
        return
    if _logging is None:
        return
    for handler in _logger.handlers:
        if isinstance(handler, _logging.FileHandler) and handler.baseFilename == target_path:
            return
    handler = _logging.FileHandler(target_path)
    formatter = _make_formatter(colorize=False)
    if formatter is not None:
        handler.setFormatter(formatter)
    _logger.addHandler(handler)


def _config_candidates(config_path: str, config_name: str) -> List[Tuple[str, str]]:
    base = os.path.join(config_path, config_name)
    return [
        ("toml", f"{base}.toml"),
        ("ini", f"{base}.ini"),
        ("json", f"{base}.json"),
        ("yaml", f"{base}.yaml"),
        ("yaml", f"{base}.yml"),
    ]


def _load_config(
    config_name: Optional[str] = None, config_path: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    config_path = config_path if config_path is not None else configPath
    config_name = config_name if config_name is not None else configName
    for fmt, path in _config_candidates(config_path, config_name):
        if os.path.isfile(path):
            data = _read_config(path, fmt)
            if data is not None:
                return data
    return None


def _select_config_target(config_path: str, config_name: str) -> Dict[str, Any]:
    for fmt, path in _config_candidates(config_path, config_name):
        if os.path.isfile(path):
            data = _read_config(path, fmt)
            if data is None:
                data = {}
            return {"format": fmt, "path": path, "data": data}
    fmt = _default_write_format()
    extension = fmt
    return {
        "format": fmt,
        "path": os.path.join(config_path, f"{config_name}.{extension}"),
        "data": {},
    }


def _default_write_format() -> str:
    for fmt, _ in _config_candidates("", ""):
        if _can_write_format(fmt):
            return fmt
    return "ini"


def _read_config(path: str, fmt: str) -> Optional[Dict[str, Any]]:
    try:
        if fmt == "toml":
            if _toml is None:
                return None
            with open(path, "rb") as handle:
                return _toml.load(handle)
        if fmt == "ini":
            parser = configparser.ConfigParser()
            parser.read(path)
            data = {"DEFAULT": dict(parser.defaults())}
            for section in parser.sections():
                data[section] = dict(parser.items(section))
            return data
        if fmt == "json":
            with open(path, "r") as handle:
                return json.load(handle)
        if fmt == "yaml":
            if _yaml is None:
                return None
            with open(path, "r") as handle:
                return _yaml.safe_load(handle) or {}
    except Exception:
        return None
    return None


def _write_config(path: str, fmt: str, data: Dict[str, Any]) -> None:
    try:
        if fmt == "toml":
            if _toml is not None and hasattr(_toml, "dump"):
                with open(path, "w") as handle:
                    _toml.dump(data, handle)
            elif _toml is not None and hasattr(_toml, "dumps"):
                with open(path, "w") as handle:
                    handle.write(_toml.dumps(data))
            else:
                with open(path, "w") as handle:
                    handle.write(_toml_dumps_simple(data))
            return
        if fmt == "ini":
            parser = configparser.ConfigParser()
            defaults = data.get("DEFAULT", {})
            if isinstance(defaults, dict):
                parser["DEFAULT"] = {str(k): str(v) for k, v in defaults.items()}
            for section, values in data.items():
                if section == "DEFAULT":
                    continue
                if not isinstance(values, dict):
                    continue
                parser[section] = {str(k): str(v) for k, v in values.items()}
            with open(path, "w") as handle:
                parser.write(handle)
            return
        if fmt == "json":
            with open(path, "w") as handle:
                json.dump(data, handle, indent=2)
            return
        if fmt == "yaml":
            if _yaml is None:
                return
            with open(path, "w") as handle:
                _yaml.safe_dump(data, handle, default_flow_style=False)
            return
    except Exception:
        return


def _get_value(data: Any, key: str) -> Any:
    if not isinstance(key, str):
        return None
    if not key:
        return None
    if isinstance(data, dict) and "DEFAULT" in data and "." not in key:
        defaults = data.get("DEFAULT")
        if isinstance(defaults, dict) and key in defaults:
            return defaults[key]
    cursor = data
    for part in key.split("."):
        if isinstance(cursor, dict) and part in cursor:
            cursor = cursor[part]
        else:
            return None
    return cursor


def _set_value(data: Dict[str, Any], key: str, value: Any, fmt: str) -> None:
    if not isinstance(key, str) or not key:
        return
    if fmt == "ini":
        parts = key.split(".")
        if len(parts) == 1:
            section = "DEFAULT"
            option = parts[0]
        else:
            section = parts[0]
            option = ".".join(parts[1:])
        if section not in data or not isinstance(data.get(section), dict):
            data[section] = {}
        data[section][option] = value
        return
    cursor = data
    parts = key.split(".")
    for part in parts[:-1]:
        if part not in cursor or not isinstance(cursor.get(part), dict):
            cursor[part] = {}
        cursor = cursor[part]
    cursor[parts[-1]] = value


def _can_write_format(fmt: str) -> bool:
    if fmt == "toml":
        return True
    if fmt == "ini":
        return True
    if fmt == "json":
        return True
    if fmt == "yaml":
        return _yaml is not None and hasattr(_yaml, "safe_dump")
    return False


def _toml_dumps_simple(data: Any) -> str:
    if not isinstance(data, dict):
        return ""

    lines: List[str] = []

    def write_table(prefix: str, table: Dict[str, Any]) -> None:
        if prefix:
            lines.append(f"[{prefix}]")
        for key, value in table.items():
            if isinstance(value, dict):
                continue
            lines.append(f"{key} = {_toml_format_value(value)}")
        lines.append("")
        for key, value in table.items():
            if isinstance(value, dict):
                next_prefix = f"{prefix}.{key}" if prefix else key
                write_table(next_prefix, value)

    write_table("", data)
    return "\n".join(lines).strip() + "\n"


def _toml_format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        rendered = ", ".join(_toml_format_value(item) for item in value)
        return f"[{rendered}]"
    text = str(value).replace("\\", "\\\\").replace("\"", "\\\"")
    return f"\"{text}\""


def main() -> None:
    set_log_level("debug")
    log(
        "warn",
        "This is a library. not a script, please import it, do not run it, unless youre trying to test the libraries features.",
    )
    log("debug", "Debug statement")
    log("info", "debug info")
    try:
        log("err", "Error")
    except Exception as e:
        print(f"Exception {e} triggered.")
    try:
        log("fatal", "Fatal Error")
    except Exception as e:
        print(f"Exception {e} triggered.")
    setConfigName("config_test")
    setConfigPath("./")
    config.set("app.name", "beeper")
    config.set("app.debug", True)
    config.set("db.host", "localhost")
    config.set("db.port", 5432)
    config.set("auth.token", "example-token")
    config.set("theme.primary", "chartreuse")
    config.set("feature_flags.teleport", False)
    config.set("nonsense.unicorn_mode", True)
    config.set("never.used_setting", "banana")
    print(config.get("app.name"))
    print(config.get("db.host"))
    print(config.get("feature_flags.teleport"))
    print(config.get("nonsense.unicorn_mode"))
    print(config.get("missing.value"))
    print(getConfig("homeserver"))


if __name__ == "__main__":
    main()

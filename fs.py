import json
import logging
from pathlib import Path
from typing import Any, Union, Dict

logger = logging.getLogger(__name__)

def read_json_file(path: Union[str, Path]) -> Any:
    """
    Read a JSON file and return its contents as a Python object (dict, list, etc.).

    :param path: Path to the JSON file.
    :return: The parsed Python object.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"No such file: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def write_json_file(path: Union[str, Path], data: Dict[str, Any], *, indent: int = 2) -> None:
    """
    Write a Python dict to a JSON file.

    :param path: Path where the JSON file will be written.
    :param data: Dictionary (or any JSON-serializable object) to dump.
    :param indent: Number of spaces to indent for pretty-printing (default: 2).
    """
    path = Path(path)
    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)
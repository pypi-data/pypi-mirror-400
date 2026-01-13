import json
from pathlib import Path
from typing import TypeVar, Type

T = TypeVar("T")


def load_json(path: Path | str, cls: Type[T] = dict) -> T:
    path = Path(path)

    with open(path, "r") as f:
        data = f.read()

    data = json.loads(data)
    return cls(**data)

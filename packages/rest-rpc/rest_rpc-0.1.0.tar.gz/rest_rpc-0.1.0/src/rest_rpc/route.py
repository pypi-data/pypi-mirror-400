import inspect
from dataclasses import dataclass

from .request_params import RequestParam


@dataclass
class Route:
    method: str
    path: str
    name: str
    signature: inspect.Signature
    raw_annotations: dict[str, type]
    raw_defaults: tuple | None
    request_params: dict[str, RequestParam]

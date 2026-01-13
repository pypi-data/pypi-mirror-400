from dataclasses import dataclass
from fnnx.ops._base import BaseOp
from typing import TypedDict


class IO(TypedDict):
    dtype: str
    shape: list[int | str]


@dataclass
class OpInstance:
    operator: BaseOp
    input_specs: IO
    output_specs: IO

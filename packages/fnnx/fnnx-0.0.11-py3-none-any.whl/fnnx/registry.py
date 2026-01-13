from typing import Type
from fnnx.ops._base import BaseOp
from fnnx.ops.onnx import OnnxOp_V1
import warnings


class Registry:

    def __init__(self):
        self.ops: dict[str, Type[BaseOp]] = {}

    def register_op(self, op: Type[BaseOp], name: str):
        self.ops[name] = op

    def get_op(self, name: str) -> Type[BaseOp]:
        return self.ops[name]

    def register_default_ops(self):
        if len(self.ops.keys()) > 0:
            warnings.warn(
                "Attempting to register default ops into a non-empty registry."
            )
        self.register_op(OnnxOp_V1, "ONNX_v1")

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from fnnx.device import DeviceConfig
from fnnx.dtypes import DtypesManager
from concurrent.futures._base import Executor


class BaseOp(ABC):
    supported_dynamic_attributes: list[str] = []
    required_dynamic_attributes: list[str] = []

    def __init__(
        self,
        artifact_path: str,
        *args,
        attributes: dict,
        dynamic_attribute_map: dict,
        device_config: DeviceConfig,
        input_specs,
        output_specs,
        dtypes_manager: DtypesManager,
        executor: Executor,
        **kwargs,
    ):
        self.dynamic_attribute_map = dynamic_attribute_map
        self._warmed_up = False
        self.artifact_path = artifact_path
        self._device_config: DeviceConfig = device_config
        self.attributes = attributes
        self.input_specs = input_specs
        self.output_specs = output_specs
        self.dtypes_manager = dtypes_manager
        self.executor = executor

    @abstractmethod
    def warmup(self, *args, **kwargs) -> BaseOp:
        pass

    @abstractmethod
    def compute(self, inputs: list, dynamic_attributes: dict, **kwargs):
        pass

    @abstractmethod
    async def compute_async(self, inputs: list, dynamic_attributes: dict, **kwargs):
        pass

    def extract_dynamic_attribute(self, dynamic_attributes: dict):

        extracted = {}
        for key, value in self.dynamic_attribute_map.items():
            source_name = value.get("name")
            default_value = value.get("default_value")
            source_value = dynamic_attributes.get(source_name, None)
            target_value = source_value or default_value
            extracted[key] = target_value
        return extracted

    def verify_required_dynamic_attributes(self, dynamic_attributes_map: dict):
        for key in self.required_dynamic_attributes:
            if key not in dynamic_attributes_map:
                raise ValueError(f"Missing required dynamic attribute: {key}")


@dataclass
class OpOutput:
    value: list[Any]
    metadata: dict | None = None

from abc import ABC, abstractmethod
from fnnx.device import DeviceMap
from dataclasses import dataclass


@dataclass
class BaseHandlerConfig:
    pass


class BaseHandler(ABC):
    @abstractmethod
    def __init__(
        self,
        model_path: str,
        device_map: DeviceMap,
        handler_config: BaseHandlerConfig | None = None,
        **kwargs,
    ):
        pass

    @abstractmethod
    def compute(self, inputs: dict, dynamic_attributes: dict) -> dict:
        pass

    @abstractmethod
    async def compute_async(self, inputs: dict, dynamic_attributes: dict) -> dict:
        pass

from dataclasses import dataclass


@dataclass
class DeviceConfig:
    accelerator: str
    device_config: dict | None


@dataclass
class DeviceMap:
    accelerator: str
    node_device_map: dict[str, dict]
    variant_device_config: dict | str | None = None

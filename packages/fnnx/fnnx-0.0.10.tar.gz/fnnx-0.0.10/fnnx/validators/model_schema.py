from fnnx.validators.jsonschema import validate_jsonschema
from fnnx.spec import schema


def validate_manifest(manifest: dict):
    validate_jsonschema(manifest, schema["manifest"])


def validate_op_instances(instances: list):
    if not isinstance(instances, list):
        raise ValueError("Nodes must be a list")
    for instance in instances:
        op_type = instance["op"]
        if op_type not in schema["ops"]:
            raise ValueError(f"Unknown op type: {op_type}")
        validate_jsonschema(instance, schema["ops"][op_type])


def validate_variant(variant: str, config: dict):
    if variant not in schema["variants"]:
        raise ValueError(f"Unknown variant: {variant}")
    validate_jsonschema(config, schema["variants"][variant])

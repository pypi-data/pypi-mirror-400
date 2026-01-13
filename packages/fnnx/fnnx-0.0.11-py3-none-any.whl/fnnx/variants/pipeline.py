from fnnx.variants._common.dag import dag_compute, dag_compute_async, DagComponent
from dataclasses import dataclass
from concurrent.futures._base import Executor
from fnnx.node_instance import OpInstance
from fnnx.variants._base import BaseVariant
from fnnx.variants._common.validators import validate_inputs


@dataclass
class PipelineNodeInstance(OpInstance, DagComponent):
    pass


class Pipeline(BaseVariant):

    def _post_init(
        self,
    ):

        self.pipeline_node_instances: list[PipelineNodeInstance] = []
        for node in self.variant_config["nodes"]:
            op_instance = self.op_instances[node["op_instance_id"]]
            self.pipeline_node_instances.append(
                PipelineNodeInstance(
                    operator=op_instance.operator,
                    inputs=node["inputs"],
                    outputs=node["outputs"],
                    input_specs=op_instance.input_specs,
                    output_specs=op_instance.output_specs,
                    extra_dynattrs=node.get("extra_dynattrs", {}),
                )
            )

    async def _node_compute_async(
        self, node_instance: PipelineNodeInstance, node_inputs, **node_passtrhough
    ):
        validate_inputs(node_inputs, node_instance.input_specs)
        return await node_instance.operator.compute_async(
            node_inputs, **node_passtrhough
        )

    def _node_compute(
        self, node_instance: PipelineNodeInstance, node_inputs, **node_passtrhough
    ):
        validate_inputs(node_inputs, node_instance.input_specs)
        return node_instance.operator.compute(node_inputs, **node_passtrhough)

    async def compute_async(
        self,
        inputs: dict,
        dynamic_attributes: dict,
    ) -> dict:

        passthrough = {
            "op_executor": self.op_executor,
            "dynamic_attributes": dynamic_attributes,
        }

        return await dag_compute_async(
            inputs,
            self.pipeline_node_instances,
            self._node_compute_async,
            as_val=lambda res: res.value,
            components_passthrough=passthrough,
        )

    def compute(
        self,
        inputs,
        dynamic_attributes: dict,
    ) -> dict:
        passthrough = {
            "op_executor": self.op_executor,
            "dynamic_attributes": dynamic_attributes,
        }

        return dag_compute(
            inputs,
            self.pipeline_node_instances,
            self.executor,
            self._node_compute,
            as_val=lambda res: res.value,
            components_passthrough=passthrough,
        )

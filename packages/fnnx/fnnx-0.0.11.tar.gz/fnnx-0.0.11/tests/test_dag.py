import unittest
import asyncio
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from dataclasses import dataclass
from fnnx.variants._common.dag import (
    dag_compute_async,
    dag_compute,
    DagComponent as Component,
)
from fnnx.variants._common.validators import validate_inputs as _validate_inputs


class TestDagFunctions(unittest.TestCase):
    def test_validate_inputs_valid(self):
        input_specs = [{"shape": (2, 2), "dtype": "Array[float64]"}]
        inputs = [np.array([[1.0, 2.0], [3.0, 4.0]])]
        try:
            _validate_inputs(inputs, input_specs)
        except Exception as e:
            self.fail(f"_validate_inputs raised an exception {e}")

    def test_validate_inputs_invalid_shape(self):
        input_specs = [{"shape": (2, 2), "dtype": "Array[float64]"}]
        inputs = [np.array([1.0, 2.0])]
        with self.assertRaises(ValueError):
            _validate_inputs(inputs, input_specs)

    def test_validate_inputs_invalid_dtype(self):
        input_specs = [{"shape": (2, 2), "dtype": "Array[int32]"}]
        inputs = [np.array([[1.0, 2.0], [3.0, 4.0]])]
        with self.assertRaises(ValueError):
            _validate_inputs(inputs, input_specs)

    async def async_compute_fn(self, component, inputs, **kwargs):
        await asyncio.sleep(0.1)
        return [np.sum(inputs[0])]

    def as_val(self, result):
        return result

    def test_dag_compute_async(self):

        inputs = {"x": np.array([1, 2, 3])}
        components = [
            Component(
                inputs=["x"],
                outputs=["y"],
                extra_dynattrs={},
            )
        ]
        components_passthrough = {}
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            dag_compute_async(
                inputs,
                components,
                self.async_compute_fn,
                self.as_val,
                components_passthrough,
            )
        )
        self.assertIn("y", result)
        self.assertEqual(result["y"], 6)

    def compute_fn(self, component, inputs, **kwargs):
        return [np.prod(inputs[0])]

    def test_dag_compute(self):

        inputs = {"x": np.array([1, 2, 3, 4])}
        components = [
            Component(
                inputs=["x"],
                outputs=["y"],
                extra_dynattrs={},
            )
        ]
        components_passthrough = {}
        graph_executor = ThreadPoolExecutor(max_workers=2)
        result = dag_compute(
            inputs,
            components,
            graph_executor,
            self.compute_fn,
            self.as_val,
            components_passthrough,
        )
        self.assertIn("y", result)
        self.assertEqual(result["y"], 24)


if __name__ == "__main__":
    unittest.main()

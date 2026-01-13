import unittest
from fnnx.registry import Registry
from fnnx.ops.onnx import OnnxOp_V1


class TestRegistry(unittest.TestCase):

    def setUp(self):
        self.registry = Registry()

    def test_initialization(self):
        self.assertEqual(self.registry.ops, {})

    def test_register_op(self):
        self.registry.register_op(OnnxOp_V1, "ONNX_v1")
        self.assertIn("ONNX_v1", self.registry.ops)
        self.assertEqual(self.registry.ops["ONNX_v1"], OnnxOp_V1)

    def test_get_op(self):
        self.registry.register_op(OnnxOp_V1, "ONNX_v1")
        op = self.registry.get_op("ONNX_v1")
        self.assertEqual(op, OnnxOp_V1)

    def test_register_default_ops(self):
        self.registry.register_default_ops()
        self.assertIn("ONNX_v1", self.registry.ops)
        self.assertEqual(self.registry.ops["ONNX_v1"], OnnxOp_V1)

    def test_register_default_ops_warning(self):
        self.registry.register_op(OnnxOp_V1, "ONNX_v1")
        with self.assertWarns(UserWarning):
            self.registry.register_default_ops()


if __name__ == "__main__":
    unittest.main()

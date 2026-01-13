from __future__ import annotations
from fnnx.ops._base import BaseOp, OpOutput
from os.path import join as pjoin

try:
    import onnxruntime as ort  # type: ignore
except ImportError:
    ort = None

try:
    from onnxruntime_extensions import get_library_path as _get_extensions_library_path  # type: ignore
except ImportError:
    _get_extensions_library_path = None

from fnnx.utils import to_thread

CPU_EXECUTION_PROVIDER = "CPUExecutionProvider"
CUDA_EXECUTION_PROVIDER = "CUDAExecutionProvider"


class OnnxOp_V1(BaseOp):
    def warmup(
        self,
    ) -> OnnxOp_V1:
        self.model_path = pjoin(self.artifact_path, "model.onnx")
        if not ort:
            raise ImportError("onnxruntime is not installed")
        if self._device_config.accelerator == "cuda":
            execution_providers = [CUDA_EXECUTION_PROVIDER, CPU_EXECUTION_PROVIDER]
        else:
            execution_providers = [CPU_EXECUTION_PROVIDER]
        session_options = ort.SessionOptions()
        if self.attributes.get("use_onnxruntime_extensions", False):
            if not _get_extensions_library_path:
                raise ImportError("onnxruntime_extensions is not installed")
            libpath = _get_extensions_library_path()
            session_options.register_custom_ops_library(libpath)
        self._sess = ort.InferenceSession(
            self.model_path, providers=execution_providers, sess_options=session_options
        )
        self._ort_inputs = [i.name for i in self._sess.get_inputs()]
        self._ort_outputs = [o.name for o in self._sess.get_outputs()]
        self._warmed_up = True
        return self

    def compute(self, inputs: list, dynamic_attributes: dict, **kwargs):
        if not self._warmed_up:
            raise RuntimeError("Op is not warmed up")
        outputs = self._sess.run(self._ort_outputs, dict(zip(self._ort_inputs, inputs)))
        return OpOutput(value=list(outputs), metadata={})

    async def compute_async(self, inputs: list, dynamic_attributes: dict, **kwargs):
        return await to_thread(self.executor, self.compute, inputs, dynamic_attributes)

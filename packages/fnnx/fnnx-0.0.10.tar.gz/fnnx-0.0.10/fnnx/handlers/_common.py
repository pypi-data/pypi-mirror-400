import os
import tarfile
import tempfile


def unpack_model(model_path: str) -> tuple[str, bool]:
    if os.path.isdir(model_path):
        return model_path, False
    with tarfile.open(model_path, "r") as tar:
        tmp_dir = tempfile.mkdtemp(prefix="fnnx_")  #
        tar.extractall(tmp_dir, filter="data")
    return tmp_dir, True

import os

from davidkhala.ai.huggingface import clone
from pathlib import Path

def bge_m3_path(git_dir: os.PathLike):
    model_dir = clone(git_dir, repo_id="BAAI/bge-m3",allow_patterns=["onnx/*"])
    onnx_path = Path(model_dir) / "onnx" / "model.onnx"
    assert onnx_path.is_file() and onnx_path.exists()
    return onnx_path

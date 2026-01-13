import os
from typing import Optional

from huggingface_hub import snapshot_download


def clone(git_dir: os.PathLike,
          *,
          owner: Optional[str] = None,
          repository: Optional[str] = None,
          repo_id: Optional[str] = None,
          **kwargs
          ) -> str:
    if not repo_id:
        repo_id = f"{owner}/{repository}"
    return snapshot_download(
        repo_id=repo_id,
        local_dir=git_dir,
        local_dir_use_symlinks=False,
        **kwargs
    )

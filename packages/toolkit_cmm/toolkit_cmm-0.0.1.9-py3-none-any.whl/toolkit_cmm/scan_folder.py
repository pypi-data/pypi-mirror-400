import os
from typing import List


def scan_folder(
    folder: str, result: List[str], exts: List[str], recursive: bool = False
) -> None:
    """
    Usage::

      result = []
      scan_folder('./',result=result,exts=['.mp4','.mkv'], recursive=True)
      print(result)
    """
    exts = [ext.lower() for ext in exts]
    for filename in os.listdir(folder):
        f = os.path.join(folder, filename)
        if os.path.isfile(f):
            root, ext = os.path.splitext(f)
            if ext.lower() in exts:
                result.append(f)
        elif os.path.isdir(f) and recursive:
            scan_folder(folder=f, result=result, exts=exts)

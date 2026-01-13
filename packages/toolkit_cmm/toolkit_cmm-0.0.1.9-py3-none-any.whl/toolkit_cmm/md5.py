def get_file_md5(path: str) -> str:
    """
    Usage::

      md5 = get_file_md5('./file')
      print(md5)
    """
    import hashlib

    m = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in f:
            m.update(chunk)
    return m.hexdigest()

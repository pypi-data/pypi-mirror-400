Overview
========

python3.8+(dev on Ubuntu)

Docs: sphinx(reStructuredText) + github pages(github action)

Packages manage: Hatch + UV

Format & Lint: ruff

Typing: mypy

Testing: pytest

Automated Testing
-----------------

运行测试：

.. code-block:: shell

  # 在 default 环境中
  hatch run test

  # 或在 test 环境中
  hatch env run -e test -- pytest
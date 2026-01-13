Dependency
==========

Install Dependencies
--------------------

.. code-block:: shell

  # 使用 Hatch
  hatch env create

  # 或使用 UV
  uv sync

Add Dependency
--------------

.. code-block:: shell

  # 编辑 pyproject.toml 中的 [project.dependencies] 或 [project.optional-dependencies]
  # 然后重新创建环境
  hatch env prune && hatch env create

  # 或使用 UV
  uv add <package>

List Dependencies
-----------------

.. code-block:: shell

  # 使用 Hatch
  hatch env run -- pip list

  # 或使用 UV
  uv tree

Export requirements.txt
-----------------------

.. code-block:: shell

  # 使用 UV 生成 lock 文件
  uv sync
  # requirements.txt 可从 uv.lock 导出，或手动创建

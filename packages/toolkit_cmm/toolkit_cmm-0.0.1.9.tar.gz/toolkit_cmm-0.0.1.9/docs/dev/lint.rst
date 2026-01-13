Linting and Formatting
========================

Code Formatting
---------------

使用 ruff 进行代码格式化。

.. code-block:: shell

  # 在 default 环境中
  hatch run format

  # 或手动
  hatch env run -- ruff format

Static Type Checking
--------------------

使用 mypy 进行类型检查。

.. code-block:: shell

  hatch env run -- mypy toolkit_cmm

Linting
-------

使用 ruff 进行代码检查。

.. code-block:: shell

  hatch run lint

  # 或手动
  hatch env run -- ruff check

Auto-fix
--------

.. code-block:: shell

  hatch env run -- ruff check --fix
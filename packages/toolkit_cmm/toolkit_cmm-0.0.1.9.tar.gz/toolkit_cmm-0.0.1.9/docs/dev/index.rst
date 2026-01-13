Developer Manual
================

.. code-block:: shell
   
   # 安装 Hatch 和 UV
   pip install hatch uv
   # 或使用 UV 安装
   uv pip install hatch

   # 创建环境并安装依赖
   hatch env create
   # 或使用 UV
   uv sync

.. toctree::
   :maxdepth: 2

   overview
   dep
   docs
   lint
   publish
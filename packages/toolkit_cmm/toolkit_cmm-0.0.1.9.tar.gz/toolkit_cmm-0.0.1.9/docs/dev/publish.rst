Publish
=======

PyPI
----

配置 PyPI token：https://pypi.org/manage/account/token/

.. code-block:: shell

  # 1. 清空 dist 文件夹
  rm -rf dist

  # 2. 修改版本号（编辑 toolkit_cmm/_version.py）
  # 例如：__version__ = "0.0.1.9"

  # 3. 构建包
  hatch build

  # 4. 检查打包内容
  tar -tf dist/*.tar.gz
  # 或 unzip -l dist/*.whl

  # 5. 发布到 PyPI
  hatch publish

Test PyPI
---------

配置 Test PyPI token：https://test.pypi.org/manage/account/token/

.. code-block:: shell

  # 1. 清空 dist 文件夹
  rm -rf dist

  # 2. 修改版本号（编辑 toolkit_cmm/_version.py）

  # 3. 构建包
  hatch build

  # 4. 检查打包内容
  tar -tf dist/*.tar.gz

  # 5. 发布到 Test PyPI
  hatch publish -r test

.. code-block:: shell

  # 测试安装
  pip install --index-url https://test.pypi.org/simple/ toolkit_cmm
  python3 -c 'from toolkit_cmm.helloworld import hello_world; print(hello_world())'

Issues
------

如果遇到认证问题，确保 token 配置正确，或使用 API token。
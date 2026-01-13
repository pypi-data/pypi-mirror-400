Docs
======

Init by `sphinx-quickstart`

Make html
---------

.. code-block:: shell

  cd docs
  make clean && make html

Serve html
----------

.. code-block:: shell
  
  python -m http.server --directory _build/html

Github workflows
----------------

https://github.com/CroMarmot/pytoolkit/settings/actions

Switch `Workflow permissions` to allow actions write to gh-pages
Advanced Usage
==========================

Build My Potc Plugin
---------------------------

Actually ``potc`` has a complete plugin support system, which is easy to operate and configure.
It can take effect after installation.

For example, here are some demo plugins

* `potc-dict <https://github.com/potc-dev/potc/tree/main/plugins/potc_dict>`_, a plugin which can make dict prettier
* `potc-torch <https://github.com/potc-dev/potc-torch>`_, a plugin which supports visualization of torch's tensor
* `potc-treevalue <https://github.com/potc-dev/potc-treevalue>`_, a plugin which support visualization of treevalue's structure

Like the ``potc-dict``, after the installation of

.. code:: shell

    pip install potc-dict

The format of dumped ``dict`` objects will be changed,
just like the `README.md of potc-dict <https://github.com/potc-dev/potc/tree/main/plugins/potc_dict/README.md>`_ said.


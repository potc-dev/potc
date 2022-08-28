CLI Usage
======================

In ``potc``, cli is provided to quickly generate python code. \
For example, you can translate an object with ``potc trans`` \
command. Firstly, here is the content of python source \
file ``data.py``

.. literalinclude:: data.py
    :language: shell
    :linenos:

Translation of Single Object
---------------------------------

Based on ``data.py``, we can translate ``v_a`` from ``data.py`` by \
this command

.. literalinclude:: cli_obj_1.demo.sh
    :language: shell
    :linenos:

The output should be

.. literalinclude:: cli_obj_1.demo.sh.txt
    :language: text
    :linenos:

Also, if you need to take a look at the full information of \
this translation, you can use ``-I`` option to display them, \
like this

.. literalinclude:: cli_obj_2.demo.sh
    :language: shell
    :linenos:

The output (including information) should be

.. literalinclude:: cli_obj_2.demo.sh.txt
    :language: text
    :linenos:

Export Multiple Objects
--------------------------------

In further cases, we may need to directly dump a runnable \
python source code and then maybe execute it. You can dump \
the variables from ``data.py`` by this command

.. literalinclude:: cli_vars_1.demo.sh
    :language: shell
    :linenos:

The dumped code should be

.. literalinclude:: cli_vars_1.demo.sh.txt
    :language: shell
    :linenos:


Besides, you can use your self-defined rules to change the \
dumping result, like this

.. literalinclude:: cli_vars_2.demo.sh
    :language: shell
    :linenos:

The new dumped code should be

.. literalinclude:: cli_vars_2.demo.sh.txt
    :language: shell
    :linenos:

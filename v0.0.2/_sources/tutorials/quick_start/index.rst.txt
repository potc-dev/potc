Quick Start
=======================

After the installation is complete, we can run some simple \
examples. This page will show you this.

Simple Translation
-----------------------

A simplest translation can be processed with the code below.

.. literalinclude:: simple.demo.py
    :language: python
    :linenos:

The output result should be

.. literalinclude:: simple.demo.py.txt
    :language: text
    :linenos:

Most of the primitive data types supported by python can be \
turned back to runnable source code with ``potc``.

Scriptable Translation
--------------------------

If we need to translate multiple values, and dump the translation \
result to a runnable ``.py`` script, we can do like this

.. literalinclude:: vars.demo.py
    :language: python
    :linenos:

The output result (as well as the dumped script) should be

.. literalinclude:: vars.demo.py.txt
    :language: python
    :linenos:

It is runnable, you can take a try.

Define My Rules
--------------------------

In the example above, ``numpy`` objects are translated as \
the serialized bytes, it is not as visible as we expected. \
Besides, you may think that the dictionary which is expressed \
with ``{}`` format is so ugly that you want to optimize the \
expression.

You can define your own rule like the example below.

.. literalinclude:: diy_rule.demo.py
    :language: python
    :linenos:

The output result (as well as the dumped script) should be

.. literalinclude:: diy_rule.demo.py.txt
    :language: python
    :linenos:

Now you can see the dictionaries will be expressed with \
``dict`` form when the keys is allowed to do so, \
the ``np.ndarray`` objects will be expressed with the \
visible format as well.


Use CLI For Translating
-------------------------------

In ``potc``, cli is provided to quickly generate python code. \
For example, you can translate an object with ``potc trans`` \
command. Firstly, here is the content of python source \
file ``data.py``

.. literalinclude:: data.py
    :language: shell
    :linenos:

based on this, we can translate ``v_a`` from ``data.py`` by \
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

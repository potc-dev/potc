Quick Start
=======================

After the installation is complete, we can run some simple \
examples. This page will show you this.

Simple Translation
-----------------------

A simplest translation can be processed with the code below.

.. literalinclude:: simple.demo.py
    :language: python

The output result should be

.. literalinclude:: simple.demo.py.txt
    :language: text

Most of the primitive data types supported by python can be \
turned back to runnable source code with ``potc``.

Scriptable Translation
--------------------------

If we need to translate multiple values, and dump the translation \
result to a runnable ``.py`` script, we can do like this

.. literalinclude:: vars.demo.py
    :language: python

The output result (as well as the dumped script) should be

.. literalinclude:: vars.demo.py.txt
    :language: python

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

The output result (as well as the dumped script) should be

.. literalinclude:: diy_rule.demo.py.txt
    :language: python

Now you can see the dictionaries will be expressed with \
``dict`` form when the keys is allowed to do so, \
the ``np.ndarray`` objects will be expressed with the \
visible format as well.


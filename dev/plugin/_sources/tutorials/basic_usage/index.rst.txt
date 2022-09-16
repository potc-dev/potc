Basic Usage
========================


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



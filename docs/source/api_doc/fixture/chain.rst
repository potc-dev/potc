potc.fixture.chain
======================

build_chain
-------------------

.. autofunction:: potc.fixture.chain.build_chain

.. note::

    In ``build_chain`` function, there are 2 main structure \
    which represents different structures:

    - list, which means the elements in it are paralleled \
      with each other.
    - tuple, which means the element in it should be in \
      order one by one.


Here are some examples about this problem.

In the simplest case, here is the difference between ``(r1, r2)`` \
and ``[r1, r2]``. In the tuple's case, it means ``t1`` must \
be processed earlier than ``t2``, while in list's case, it \
just means they are put together here without orders' limit.

.. image:: chain_simple.gv.svg
    :align: center

In another case of ``(r1, [(r2, r3), (r4, r5)], r6)``, its order \
graph should be like below.

.. image:: chain_another.gv.svg
    :align: center

Actually, ``r1`` should be ahead of ``[(r2, r3), (r4, r5)]``, \
``r2`` should be ahead of ``r3``, ``r4`` should be ahead of \
``r5``, ``[(r2, r3), (r4, r5)]`` should be ahead of ``r6``. \
So one of the final order should be ``[r1, r2, r4, r5, r3, r6]`` \
(the valid orders are not unique in this case).


rules_combine
-------------------

.. autofunction:: potc.fixture.chain.rules_combine



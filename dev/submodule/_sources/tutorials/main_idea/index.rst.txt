Main Idea
=======================

Why potc is designed?
----------------------------

In practical applications, we often need to export or visualize an existing python object,
and we need to ensure that the exported product has clear and visible meaning and can be loaded correctly
by the python interpreter again after modification. However, the existing data serialization tools
are difficult to make the exported data still clearly visible, so they can not support modification.
Based on this requirement, Potc provides a method to convert existing python objects into runnable python code,
as shown in the following figure

.. image:: potc-doing.svg
    :align: center

Therefore, it is obvious that what ``potc`` does is to convert existing python objects into source
code that can run and support import.

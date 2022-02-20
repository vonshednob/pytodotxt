Usage Examples
==============


Adding a task to a todo.txt file
--------------------------------

.. literalinclude:: ../../examples/adding_task.py
   :linenos:
   :language: python

Instead of calling ``todotxt.add``, you could of course also just call
``todotxt.tasks.append``, but ``add`` will conveniently update
``new_task.todotxt`` and ``linenr``.


Mark all tasks of a file as completed
-------------------------------------

.. literalinclude:: ../../examples/complete_tasks.py
   :linenos:
   :language: python


Have your own custom Task subclass
----------------------------------

.. literalinclude:: ../../examples/custom_task.py
   :linenos:
   :language: python


pytodotxt
=========

.. toctree::
   :maxdepth: 1

   install
   changelog
   examples
   contributors
   license
   reference

*pytodotxt* is a small library to access todo.txt-like task lists in a
convenient manner from Python.

The quickest possible way to use pytodotxt is to install it through pypi::

  pip install pytodotxt

And then access a ``todo.txt`` through Python like this, for example to
print all tasks that are not completed yet:

.. code:: python

   import pytodotxt

   todotxt = pytodotxt.TodoTxt('todo.txt')
   todotxt.parse()

   for task in todotxt.tasks:
       if not task.is_completed:
           print(task.description)


There are `more examples available <examples.html>`_, but if you prefer, there’s
also the full `API reference here <reference.html>`_.


# pytodotxt

A tiny library to access todo.txt-like task lists.


## Installation

To install pytodotxt, you can follow these steps to clone the repository,
and install the program.

    pip install pytodotxt

That’s all there is to do.


## Documentation

You can find the full documentation at <https://vonshednob.cc/pytodotxt/doc/>.


## Example usage

Here’s an example how to open a todo.txt file and print the description of all
tasks that are not marked as completed:

    import pytodotxt


    todotxt = pytodotxt.TodoTxt('todo.txt')
    todotxt.parse()

    for task in todotxt.tasks:
        if not task.is_completed:
            print(task.description)


Here is how you add a new task to an existing todo.txt file:

    import datetime

    import pytodotxt

    todotxt = pytodotxt.TodoTxt('todo.txt')
    todotxt.parse()

    task = pytodotxt.Task()
    task.parse('This is a new task')
    task.creation_date = datetime.date.today()

    todotxt.tasks.append(task)

    todotxt.save()


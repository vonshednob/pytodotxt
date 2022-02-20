"""How to customize your task class"""
import pytodotxt


class MyTask(pytodotxt.Task): pass


todotxt = pytodotxt.TodoTxt("todo.txt",
                            parser=pytodotxt.TodoTxtParser(task_type=MyTask))

for task in todotxt.parse():
    assert isinstance(task, MyTask)

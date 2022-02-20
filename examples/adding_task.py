"""Example how to add a task to an existing todo.txt file"""
import pytodotxt


todotxt = pytodotxt.TodoTxt("todo.txt")
todotxt.parse()

new_task = pytodotxt.Task("(A) Do some more stuff")
todotxt.add(new_task)

todotxt.save()

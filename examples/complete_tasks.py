"""How to mark tasks as completed"""
import datetime

import pytodotxt


todotxt = pytodotxt.TodoTxt("todo.txt")
todotxt.parse()

for task in todotxt.parse():
    if task.is_completed:
        continue

    task.completion_date = datetime.date.today()
    task.is_completed = True

todotxt.save()

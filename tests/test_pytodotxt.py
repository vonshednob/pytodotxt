import datetime
import tempfile
import unittest
import os
from pathlib import Path

import pytodotxt


class TestFormats(unittest.TestCase):
    def test_blank(self):
        task = pytodotxt.Task()
        self.assertIsNone(task.description, "")
        self.assertEqual(task.bare_description(), "")

    def test_empty(self):
        task = pytodotxt.Task("")
        self.assertIsNone(task.description, "")
        self.assertEqual(task.bare_description(), "")

    def test_basic_todo1(self):
        line = "Some task"
        task = pytodotxt.Task(line)
        self.assertEqual(task.description, line)

    def test_basic_todo2(self):
        line = 'x 2016-05-20 (A) 2016-04-30 measure space for +chapelShelving @chapel due:2016-05-30'
        task = pytodotxt.Task(line)
        self.assertEqual(task.priority, "A")
        self.assertEqual(task.completion_date, datetime.date(2016, 5, 20))
        self.assertEqual(task.creation_date, datetime.date(2016, 4, 30))
        self.assertEqual(task.projects, ["chapelShelving"])
        self.assertEqual(task.contexts, ["chapel"])
        self.assertEqual(task.attributes, {"due": ["2016-05-30"]})
        self.assertEqual(task.description, "measure space for +chapelShelving @chapel due:2016-05-30")

    def test_basic_todo3(self):
        task = pytodotxt.Task('x completed +task with @multiple weird @contexts')
        self.assertEqual(task.contexts, ["multiple", "contexts"])

    def test_basic_todo4(self):
        task = pytodotxt.Task('task with +1Interesting_%project-/name? and more')
        self.assertEqual(task.projects, ["1Interesting_%project-/name?"])

    def test_keywords1(self):
        task = pytodotxt.Task("fancy task with many:yes keywords:of-course fancy:maybe")
        self.assertEqual(task.attributes, {'many': ['yes'],
                                           'keywords': ['of-course'],
                                           'fancy': ['maybe']})

    def test_keywords2(self):
        task = pytodotxt.Task("weird:yes task with weird:maybe attributes")
        self.assertEqual(task.attributes, {'weird': ['yes', 'maybe']})

    def test_done(self):
        task = pytodotxt.Task("x Some task")
        self.assertTrue(task.is_completed)

    def test_not_done(self):
        task = pytodotxt.Task("Some task")
        self.assertFalse(task.is_completed)

    def test_not_done2(self):
        task = pytodotxt.Task("xSome task")
        self.assertFalse(task.is_completed)

    def test_context1(self):
        task = pytodotxt.Task("Some @context")
        self.assertEqual(task.contexts, ["context"])

    def test_context2(self):
        task = pytodotxt.Task("Some @context within")
        self.assertEqual(task.contexts, ["context"])

    def test_context3(self):
        task = pytodotxt.Task("@Some @context within")
        self.assertEqual(task.contexts, ["Some", "context"])

    def test_project1(self):
        task = pytodotxt.Task("And a +project")
        self.assertEqual(task.projects, ["project"])

    def test_project2(self):
        task = pytodotxt.Task("And a +project within")
        self.assertEqual(task.projects, ["project"])

    def test_project3(self):
        task = pytodotxt.Task("+project needs to be done")
        self.assertEqual(task.projects, ["project"])

    def test_project4(self):
        task = pytodotxt.Task("+task")
        self.assertEqual(task.description, "+task")
        self.assertEqual(task.bare_description(), "")

    def test_priority1(self):
        task = pytodotxt.Task("x (A) task with priority")
        self.assertEqual(task.priority, "A")

    def test_priority2(self):
        task = pytodotxt.Task("(b) task without priority")
        self.assertIsNone(task.priority)

    def test_priority3(self):
        task = pytodotxt.Task("x 2018-04-12 (H) task with priority")
        self.assertEqual(task.priority, "H")

    def test_priority4(self):
        task = pytodotxt.Task("(X) 2010-07-07 @task with +priority")
        self.assertEqual(task.priority, "X")

    def test_creation_date1(self):
        task = pytodotxt.Task("2009-02-01 This is February!")
        self.assertEqual(task.creation_date, datetime.date(2009, 2, 1))

    def test_creation_date2(self):
        task = pytodotxt.Task("x 2009-03-01 2009-02-01 This is February!")
        self.assertEqual(task.creation_date, datetime.date(2009, 2, 1))

    def test_creation_date3(self):
        task = pytodotxt.Task("x 2009-03-01 (A) 2009-02-01 This is February!")
        self.assertEqual(task.creation_date, datetime.date(2009, 2, 1))

    def test_creation_date4(self):
        task = pytodotxt.Task("(B) 2009-02-01 This is February!")
        self.assertEqual(task.creation_date, datetime.date(2009, 2, 1))

    def test_completion_date1(self):
        task = pytodotxt.Task("(A) 2009-02-01 This is February!")
        self.assertIsNone(task.completion_date)
        self.assertEqual(task.creation_date, datetime.date(2009, 2, 1))

    def test_completion_date2(self):
        task = pytodotxt.Task("x 2009-03-01 (A) 2009-02-01 This is February!")
        self.assertEqual(task.completion_date, datetime.date(2009, 3, 1))

    def test_completion_date3(self):
        task = pytodotxt.Task("x 2009-03-01 (A) 2009-02-01 This is February!")
        self.assertEqual(task.completion_date, datetime.date(2009, 3, 1))

    def test_completion_date4(self):
        task = pytodotxt.Task("x 2009-03-01 (A) This is February!")
        self.assertEqual(task.completion_date, datetime.date(2009, 3, 1))

    def test_completion_date5(self):
        task = pytodotxt.Task("x (A) 2009-03-01 This is February!")
        self.assertIsNone(task.completion_date)

    def test_completion_date6(self):
        task = pytodotxt.Task("x 2010-10-11 Party on 10-10-10")
        self.assertTrue(task.is_completed)
        self.assertIsNone(task.creation_date)
        self.assertEqual(task.completion_date, datetime.date(2010, 10, 11))

    def test_only_date(self):
        task = pytodotxt.Task("2010-07-01")
        self.assertFalse(task.is_completed)
        self.assertIsNotNone(task.creation_date)
        self.assertEqual(len(task.attributes), 0)
        self.assertIsNone(task.priority)

    def test_attr_parsing(self):
        task = pytodotxt.Task("fancy task with many:yes keywords:of-course fancy:maybe many:oh_yeah")
        self.assertEqual(len(task.attributes), 3)
        self.assertIn('many', task.attributes)
        self.assertIn('keywords', task.attributes)
        self.assertIn('fancy', task.attributes)
        self.assertNotIn('other', task.attributes)
        self.assertEqual(len(task.attributes['many']), 2)
        self.assertEqual(len(task.attributes['fancy']), 1)

    def test_convenient_attr_parsing(self):
        task = pytodotxt.Task("fancy task with many:yes keywords:of-course fancy:maybe many:oh_yeah")
        self.assertEqual(len(task.attributes), 3)
        self.assertEqual(len(task.attr_many), 2)
        self.assertEqual(len(task.attr_fancy), 1)
        self.assertEqual(len(task.attr_not_here), 0)
        with self.assertRaises(AttributeError):
            _ = task.not_here

    def test_bare_description(self):
        task = pytodotxt.Task("(B) 2021-05-12 @computer Task with context and +project that's due:2021-12-30 soon")
        self.assertEqual(task.bare_description(), "Task with context and that's soon")

    def test_http_attribute(self):
        task = pytodotxt.Task("a task with a link to remind me +bookmark @home https://example.org/")
        self.assertEqual(task.attributes, {})
        self.assertEqual(task.bare_description(), "a task with a link to remind me https://example.org/")

    def test_str_parsing(self):
        parser = pytodotxt.TodoTxtParser()
        tasks = parser.parse("""one task\r\ntwo tasks\r\nthree tasks\r\n""")
        self.assertEqual(len(tasks), 3)
        self.assertEqual(parser.linesep, "\r\n")

    def test_bytes_parsing(self):
        parser = pytodotxt.TodoTxtParser()
        tasks = parser.parse(bytes("""one task\rtwo tasks\rthree tasks\r""", 'ascii'))
        self.assertEqual(len(tasks), 3)
        self.assertEqual(parser.linesep, "\r")


class TestManipulation(unittest.TestCase):
    def test_remove_project(self):
        task = pytodotxt.Task("Some +project in @project")
        self.assertEqual(task.projects, ["project"])
        self.assertEqual(task.contexts, ["project"])
        task.remove_project('project')
        self.assertEqual(task.projects, [])
        self.assertEqual(task.contexts, ['project'])
        self.assertEqual(str(task), "Some in @project")

    def test_replace_project(self):
        task = pytodotxt.Task("Some +project in @project")
        self.assertEqual(task.projects, ["project"])
        self.assertEqual(task.contexts, ["project"])

        task.replace_project('project', 'stuff')
        self.assertEqual(task.projects, ['stuff'])
        self.assertEqual(task.contexts, ['project'])
        self.assertEqual(str(task), "Some +stuff in @project")

    def test_replace_keyvalue(self):
        task = pytodotxt.Task("Important +project due:today due:tomorrow what? t:yesterday")
        self.assertEqual(task.attributes, {'due': ['today', 'tomorrow'],
                                           't': ['yesterday']})

        self.assertFalse(task.replace_attribute('due', 'sometime', 'tomorrow'))
        self.assertTrue(task.replace_attribute('due', 'tomorrow', '1995-10-03'))
        self.assertEqual(task.attributes, {'due': ['today', '1995-10-03'],
                                           't': ['yesterday']})
        self.assertEqual(str(task),
                         "Important +project due:today due:1995-10-03 what? t:yesterday")

    def test_attr_update_parsing(self):
        task = pytodotxt.Task("fancy task with keywords:of-course")
        self.assertEqual(len(task.attributes), 1)
        self.assertIn('keywords', task.attributes)
        self.assertNotIn('other', task.attributes)

        task.add_attribute('fruit', 'tomato')
        self.assertEqual(len(task.attributes), 2)
        self.assertIn('fruit', task.attributes)
        self.assertEqual(len(task.attributes['fruit']), 1)

    def test_completion_date(self):
        task = pytodotxt.Task("odd task")
        task.is_completed = True
        task.completion_date = datetime.date.today()

        self.assertEqual('x odd task', str(task))


class TaskWithRsync(pytodotxt.Task):
    KEYVALUE_ALLOW = pytodotxt.Task.KEYVALUE_ALLOW.union({"rsync"})


class TestSubclass(unittest.TestCase):

    def test_without_subclass_fails(self):
        task = pytodotxt.Task("sync with rsync://my.nas")
        self.assertEqual(task.bare_description(), "sync with")
        # 'fails' to detect rsync since its not in the allowed attrs
        self.assertEqual(task.attributes, {"rsync": ["//my.nas"]})

    def test_with_subclass_succeeds(self):
        task = TaskWithRsync("sync with rsync://my.nas")
        self.assertEqual(task.attributes, {})
        self.assertEqual(task.bare_description(), "sync with rsync://my.nas")

    def test_todotxt_with_subclass(self):
        with tempfile.NamedTemporaryFile() as tf:
            with open(tf.name, "w") as f:
                f.write("sync with rsync://my.nas\n")

            # shouldnt detect rsync
            txtfile_base = pytodotxt.TodoTxt(tf.name)
            task_base = txtfile_base.parse()[0]
            self.assertEqual(task_base.bare_description(), "sync with")
            self.assertEqual(task_base.attributes, {"rsync": ["//my.nas"]})

            # parse each Task in the file w/ TaskWithRsync
            txtfile_rsync = pytodotxt.TodoTxt(tf.name,
                                              parser=pytodotxt.TodoTxtParser(task_type=TaskWithRsync))
            task_rsync = txtfile_rsync.parse()[0]
            self.assertEqual(task_rsync.bare_description(), "sync with rsync://my.nas")
            self.assertEqual(task_rsync.attributes, {})


class TestEmptyOnDisk(unittest.TestCase):
    def setUp(self):
        self.tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
        self.tmpfile.close()

    def tearDown(self):
        os.unlink(self.tmpfile.name)

    def test_no_content(self):
        todotxt = pytodotxt.TodoTxt(self.tmpfile.name)
        self.assertEqual(len(todotxt.tasks), 0)

        todotxt.save()
        self.assertEqual(Path(self.tmpfile.name).read_text(encoding='utf-8'),
                         "")

    def test_add_first(self):
        todotxt = pytodotxt.TodoTxt(self.tmpfile.name)
        self.assertEqual(len(todotxt.tasks), 0)

        task = pytodotxt.Task("Some task")
        todotxt.add(task)
        todotxt.save()

        self.assertEqual(Path(self.tmpfile.name).read_text(encoding="utf-8"),
                         "Some task" + os.linesep)

    def test_blank_newlines(self):
        Path(self.tmpfile.name).write_text("\n\n", encoding='utf-8')
        todotxt = pytodotxt.TodoTxt(self.tmpfile.name)
        self.assertEqual(len(todotxt.tasks), 0)


if __name__ == '__main__':
    unittest.main()

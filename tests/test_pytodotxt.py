import datetime
import unittest

import pytodotxt


class TestFormats(unittest.TestCase):
    def test_empty(self):
        task = pytodotxt.Task("")
        self.assertIsNone(task.description, "")

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


if __name__ == '__main__':
    unittest.main()


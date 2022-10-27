"""Task class and task related constants and helpers"""
import datetime
import re


class Task:
    """A task of a todo.txt file

    The usual way to create a task is to create it from an initial string::

        task = Task("(B) some task")

    or::

        task = Task()
        task.parse("(B) some task")

    The inverse operation to parsing is to convert the task to a string::

        task = Task("(B) some task")
        assert str(task) == "(B) some task"

    """
    COMPLETED_RE = re.compile(r'^x\s+')
    PRIORITY_RE = re.compile(r'^\s*\(([A-Z]+)\)')
    PROJECT_RE = re.compile(r'(\s+|^)\+([^\s]+)')
    CONTEXT_RE = re.compile(r'(\s+|^)@([^\s]+)')
    KEYVALUE_RE = re.compile(r'(\s+|^)([^\s]+):([^\s$]+)')
    DATE_RE = re.compile(r'^\s*([\d]{4}-[\d]{2}-[\d]{2})', re.ASCII)
    DATE_FMT = '%Y-%m-%d'
    KEYVALUE_ALLOW = set(['http', 'https', 'mailto', 'ssh', 'ftp'])

    def __init__(self, line=None, linenr=None, todotxt=None):
        """Create a new task

        If no parameters are provided, an empty task is created.

        You may provide a todo.txtlike textual representation of a task
        with the ``line`` parameter, which will be parsed and all properties
        will be set accordingly.

        In case this task belongs to a container file (``todotxt`` parameter),
        you can provide the ``linenr``, if you want to be able to refer to
        it later-on.

        Both ``todotxt`` and ``linenr`` parameter are entirely optional and
        are not connected to any functionality in this class’s functions.

        To access ``key:value`` attributes of the task, you can use the
        convenience notion of ``task['attr_key']`` which will always result
        in a list. If the task doesn’t have the ``key`` attribute that list
        will be empty though.

        :param line: is the raw string representation (one line of a todo.txt
                     file).
        :param linenr: is the line number within the ``todotxt`` file, if any.
                       This is purely optional.
        :param todotxt: the ``TodoTxt`` container to which this task belongs,
                        if any.
        :type todotxt: ``None`` or ``TodoTxt``.
        """

        self.description = None
        """The descriptive portion of the task (i.e. without the completion
        marker, dates, and priority)"""

        self.is_completed = None
        """Whether or not the task is completed"""

        self.priority = None
        """Priority of the task, or ``None`` if no priority given"""

        self.completion_date = None
        """``datetime.date`` of when the task was completed, or ``None``
        if no completion date given"""

        self.creation_date = None
        """``datetime.date`` of when the task was created, or ``None``
        if no creation date given"""

        self.linenr = linenr
        """Line number of this task within its todo.txt file (0-based; the
        first task of a file will have ``self.linenr == 0``). Do not count on
        this always being set!"""

        self.todotxt = todotxt
        """The ``TodoTxt`` instance that this task belongs to. Do not count on
        this always being set!"""

        self._raw = None
        self._attributes = None

        if line is not None and len(line.strip()) > 0:
            self.parse(line)

    def remove_project(self, project):
        """Remove the first ``+project`` attribute from the description.

        :param project: the name of the project attribute to remove,
                        without the leading ``+``
        :return: ``True`` on success, otherwise ``False``.
        """
        return self.remove_tag(project, type(self).PROJECT_RE)

    def remove_context(self, context):
        """Remove the first ``@context`` attribute from the description.
        
        :param context: the name of the context attribute to remove,
                        without the leading ``@``.
        :return: ``True`` on success, otherwise ``False``.
        """
        return self.remove_tag(context, type(self).CONTEXT_RE)

    def remove_attribute(self, key, value=None):
        """Remove attribute ``key`` from the task

        If you provide a ``value`` only the attribute with that key
        and value is removed.
        If no ``value`` is provided all attributes with that key are removed.

        :param key: The name of the attribute to remove.
        :param value: The value of the attribute to remove.
        :return: ``True`` on success, otherwise ``False``
        """
        if self.description is None:
            return False

        success = False
        while True:
            key_found = False
            for match in self.parse_tags(type(self).KEYVALUE_RE):
                if key == match.group(2) and (value == match.group(3) or value is None):
                    key_found = True
                    start, end = match.span()
                    self.description = self.description[:start] + self.description[end:]
                    self.parse(str(self))
                    success = True
                    break

            if not key_found:
                break

        return success

    def remove_tag(self, text, regex):
        """Remove the first attribute ``text`` from the description

        :param regex: The regular expression to use for matching the right
                      type of attribute."""
        if self.description is None:
            return False

        for match in self.parse_tags(regex):
            if match.group(2) == text:
                start, end = match.span()
                self.description = self.description[:start] + self.description[end:]
                self.parse(str(self))
                return True
        return False

    def replace_attribute(self, key, value, newvalue):
        """Replace the value of key:value in place with key:newvalue"""
        if self.description is None:
            return False

        for match in self.parse_tags(type(self).KEYVALUE_RE):
            if key != match.group(2) or value != match.group(3):
                continue

            self.description = self.description[:match.start(3)] + \
                               newvalue + \
                               self.description[match.end(3):]
            self.parse(str(self))
            return True

        return False

    def replace_context(self, context, newcontext):
        """Replace the first occurrence of @context with @newcontext"""
        return self.replace_tag(context, newcontext, type(self).CONTEXT_RE)

    def replace_project(self, project, newproject):
        """Replace the first occurrence of @project with @newproject"""
        return self.replace_tag(project, newproject, type(self).PROJECT_RE)

    def replace_tag(self, value, newvalue, regex):
        """Replace the first ``value`` attribute with ``newvalue``

        :param regex: the regular expression to use for matching the right
                      type of attribute"""
        if self.description is None:
            return False

        for match in self.parse_tags(regex):
            if match.group(2) == value:
                self.description = self.description[:match.start(2)] + \
                                   newvalue + \
                                   self.description[match.end(2):]
                self.parse(str(self))
                return True
        return False

    def add_project(self, project):
        """Add ``+project`` to the end of the task

        :param project: the name of the project, without the leading ``+``
        """
        self.append('+' + project)
        self.parse(str(self))

    def add_context(self, context):
        """Add ``@context`` to the end of the task

        :param context: the name of the project, without the leading ``@``
        """
        self.append('@' + context)
        self.parse(str(self))

    def add_attribute(self, key, value):
        """Add the ``key:value`` attribute to the end of the task"""
        self.append(f'{key}:{value}')
        self.parse(str(self))

    def append(self, text, add_space=True):
        """Append ``text`` to the end of the task

        :param text: The text to append
        :param add_space: Whether or not to add a space before ``text``.
        """
        if self.description is None:
            self.description = text
        else:
            if add_space and not self.description.endswith(' '):
                self.description += ' '
            self.description += text
        self.parse(str(self))

    def bare_description(self):
        """The description of the task without contexts, projects or other attributes

        Some parts of the description may look like attributes, but are not,
        like URLs. To make sure that these are not stripped from the
        description, add them to ``KEYVALUE_ALLOW``.
        """
        if self.description is None:
            return ''

        parts = []
        for part in self.description.split(' '):
            if len(part) == 0 or part[0] in '@+':
                continue
            # make sure attributes with keys in KEYVALUE_ALLOW are included in bare description
            elif ':' in part:
                attribute_key = part[:part.index(":")]
                if attribute_key.lower() in type(self).KEYVALUE_ALLOW:
                    parts.append(part)
            else:
                parts.append(part)

        return ' '.join(parts)

    @property
    def projects(self):
        """A list of all ``+project`` attributes"""
        return [match.group(2) for match in self.parse_tags(type(self).PROJECT_RE)]

    @property
    def contexts(self):
        """A list of all ``@context`` attributes"""
        return [match.group(2) for match in self.parse_tags(type(self).CONTEXT_RE)]

    @property
    def attributes(self):
        """A dict of all ``key:values`` attributes

        The values portion of the dictionary is always a list.
        """
        if self._attributes is None:
            self.parse_attributes()
        return self._attributes

    def __getattr__(self, name, fallback=None):
        if name.startswith('attr_'):
            if fallback is None:
                fallback = []
            _, attrname = name.split('_', 1)
            return self.attributes.get(attrname, fallback)
        raise AttributeError(name)

    def parse_attributes(self):
        self._attributes = {}
        for match in self.parse_tags(type(self).KEYVALUE_RE):
            key = match.group(2)
            value = match.group(3)
            if key.lower() in type(self).KEYVALUE_ALLOW:
                continue
            if key not in self._attributes:
                self._attributes[key] = []
            self._attributes[key].append(value)

    def parse_tags(self, regex):
        matches = []
        if self.description is None:
            return matches

        for match in regex.finditer(self.description):
            if match:
                matches.append(match)
            else:
                break
        return matches

    def parse_priority(self, line):
        self.priority = None
        match = type(self).PRIORITY_RE.match(line)
        if match:
            self.priority = match.group(1)
            line = line[match.span()[1]:]
        return line

    @classmethod
    def match_date(cls, line):
        match = cls.DATE_RE.match(line)
        date = None
        if match:
            date = cls.parse_date(match.group(1))
            line = line[match.span()[1]:]
        return line, date

    @classmethod
    def parse_date(cls, text):
        return datetime.datetime.strptime(text, cls.DATE_FMT).date()

    def parse(self, line):
        """(Re)parse the task

        ``line`` is the raw string representation of a task, i.e. one line
        of a todo.txt file.
        """
        self._raw = line
        line = line.strip()

        # completed or not
        match = type(self).COMPLETED_RE.match(line)
        self.is_completed = match is not None
        if match:
            # strip the leading mark
            line = line[match.span()[1]:]

        if self.is_completed:
            line, self.completion_date = type(self).match_date(line)

        line = self.parse_priority(line)
        line, self.creation_date = type(self).match_date(line)

        # description
        if len(line) > 0:
            self.description = line.strip()

        self.parse_attributes()

    def __str__(self):
        """The todo.txt compatible representation of this task."""
        result = []
        if self.is_completed:
            result.append('x')

            if self.completion_date is not None and \
               self.creation_date is not None:
                result.append(self.completion_date.strftime(type(self).DATE_FMT))

        if self.priority:
            if not self.is_completed:
                result.append(f'({self.priority})')

        if self.creation_date is not None:
            result.append(self.creation_date.strftime(type(self).DATE_FMT))

        if self.description is not None:
            result.append(self.description)

        return ' '.join(result)

    def __repr__(self):
        return f'{type(self).__name__}({repr(str(self))})'


# for backwards compatibility
match_date = Task.match_date
parse_date = Task.parse_date

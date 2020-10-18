import datetime
import re
import pathlib
import os
import tempfile


class TodoTxt:
    def __init__(self, filename):
        self.filename = pathlib.Path(filename)
        self.tasks = []

    def parse(self):
        self.tasks = []

        with open(self.filename, 'rt') as fd:
            for linenr, line in enumerate(fd.readlines()):
                if len(line.strip()) == 0:
                    continue
                task = Task(line, linenr=linenr, todotxt=self)
                self.tasks.append(task)

        return self.tasks

    def save(self, target=None, safe=True):
        if target is None:
            target = self.filename
        else:
            target = pathlib.Path(target)
        write_to = target

        if safe:
            tmpfile = tempfile.NamedTemporaryFile(dir=self.filename.parent, delete=False)
            write_to = tmpfile.name
            tmpfile.close()

        with open(write_to, 'wb', buffering=0) as fd:
            lines = [str(task) + '\r\n' for task in
                     sorted(self.tasks, key=lambda t: t.linenr if t.linenr is not None else len(self.tasks))]
            fd.write(bytes(''.join(lines), 'utf-8'))

        if safe:
            os.replace(write_to, target)


class Task:
    COMPLETED_RE = re.compile(r'^x\s+')
    PRIORITY_RE = re.compile(r'^\s*\(([A-Z]+)\)')
    PROJECT_RE = re.compile(r'(\s+|^)\+([^\s]+)')
    CONTEXT_RE = re.compile(r'(\s+|^)@([^\s]+)')
    KEYVALUE_RE = re.compile(r'(\s+|^)([^\s]+):([^\s$]+)')
    DATE_RE = re.compile(r'^\s*([\d]{4}-[\d]{2}-[\d]{2})', re.ASCII)
    DATE_FMT = '%Y-%m-%d'

    def __init__(self, line=None, linenr=None, todotxt=None):
        self.description = None
        self.is_completed = None
        self.priority = None
        self.completion_date = None
        self.creation_date = None
        self.linenr = linenr
        self.raw = None
        self.todotxt = todotxt
        self._attributes = None

        if len(line.strip()) > 0:
            self.parse(line)

    def remove_project(self, project):
        return self.remove_tag(project, Task.PROJECT_RE)

    def remove_context(self, context):
        return self.remove_tag(context, Task.CONTEXT_RE)

    def remove_attribute(self, key, value=None):
        """Remove attribute `key` from the task
        If you provide a `value` only the attribute with that key and value is removed.
        If no `value` is provided all attributes with that key are removed.
        """
        success = False
        while True:
            key_found = False

            for match in self.parse_tags(Task.KEYVALUE_RE):
                if key != match.group(2):
                    continue
                
                key_found = True
                
                if value is None or match.group(3) == value:
                    start, end = match.span()
                    self.description = self.description[:start]
                    self.parse(str(self))
                    success = True

                break

            if not key_found:
                break

        return success

    def remove_tag(self, text, regex):
        for match in self.parse_tags(regex):
            if match.group(2) == text:
                start, end = match.span()
                self.description = self.description[:start] + self.description[end:]
                self.parse(str(self))
                return True
        return False

    def replace_attribute(self, key, value, newvalue):
        """Replace the value of key:value in place with key:newvalue"""
        for match in self.parse_tags(Task.KEYVALUE_RE):
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
        return self.replace_tag(context, newcontext, Task.CONTEXT_RE)

    def replace_project(self, project, newproject):
        """Replace the first occurrence of @project with @newproject"""
        return self.replace_tag(project, newproject, Task.PROJECT_RE)

    def replace_tag(self, value, newvalue, regex):
        for match in self.parse_tags(regex):
            if match.group(2) == value:
                self.description = self.description[:match.start(2)] + \
                                   newvalue + \
                                   self.description[match.end(2):]
                self.parse(str(self))
                return True
        return False

    def add_project(self, project):
        self.description += ' +' + project
        self.parse(str(self))

    def add_context(self, context):
        self.description += ' @' + context
        self.parse(str(self))

    def add_attribute(self, key, value):
        self.description += f' {key}:{value}'
        self.parse(str(self))

    @property
    def projects(self):
        return [match.group(2) for match in self.parse_tags(Task.PROJECT_RE)]

    @property
    def contexts(self):
        return [match.group(2) for match in self.parse_tags(Task.CONTEXT_RE)]

    @property
    def attributes(self):
        if self._attributes is None:
            self.parse_attributes()
        return self._attributes

    def __getattr__(self, name, fallback=None):
        if name.startswith('attr_'):
            if fallback is None:
                fallback = []
            _, attrname = name.split('_', 1)
            return self.attributes.get(attrname, fallback)
        return AttributeError(name)

    def parse_attributes(self):
        self._attributes = {}
        for match in self.parse_tags(Task.KEYVALUE_RE):
            key = match.group(2)
            value = match.group(3)
            if key in ['http', 'https', 'mailto', 'ssh', 'ftp']:
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
        match = Task.PRIORITY_RE.match(line)
        if match:
            self.priority = match.group(1)
            line = line[match.span()[1]:]
        return line

    def parse(self, line):
        self.raw = line
        line = line.strip()

        # completed or not
        match = Task.COMPLETED_RE.match(line)
        self.is_completed = match is not None
        if match:
            # strip the leading mark
            line = line[match.span()[1]:]
        
        if self.is_completed:
            line, self.completion_date = match_date(line)

        line = self.parse_priority(line)
        line, self.creation_date = match_date(line)

        # description
        if len(line) > 0:
            self.description = line.strip()

        self.parse_attributes()

    def __str__(self):
        result = ''
        if self.is_completed:
            result += 'x '

            if self.completion_date is not None:
                result += self.completion_date.strftime(Task.DATE_FMT) + ' '

        if self.priority:
            if not self.is_completed:
                result += f'({self.priority}) '

        if self.creation_date is not None:
            result += self.creation_date.strftime(Task.DATE_FMT) + ' '

        if self.description:
            result += self.description

        return result


def match_date(line):
    match = Task.DATE_RE.match(line)
    date = None
    if match:
        date = parse_date(match.group(1))
        line = line[match.span()[1]:]
    return line, date


def parse_date(text):
    return datetime.datetime.strptime(text, Task.DATE_FMT).date()


"""TodoTxt class and parser
"""
import pathlib
import tempfile
import os
import io

from .task import Task


class TodoTxt:
    """Convenience wrapper for a single todo.txt file

    The most common use is::

        todotxt = TodoTxt("todo.txt")
        todotxt.parse()

    Use the ``tasks`` property to access the parsed entries.
    """
    def __init__(self, filename, encoding='utf-8', parser=None):
        """Create a new TodoTxt instance from ``filename``

        :param filename: the file you wish to use
        :type filename: ``str`` or ``pathlib.Path``
        :param encoding: what encoding to assume for the content of the file
        :param parser: This may be a custom parser instance to use
                       instead of the default ``TodoTxtParser``.
        :type parser: ``TodoTxtParser``
        """
        self.filename = pathlib.Path(filename)
        self.encoding = encoding
        self.linesep = os.linesep

        self.tasks = []
        """The tasks of this file"""

        self.parser = parser or TodoTxtParser(self.encoding)

    def add(self, task):
        """Add a task to this container

        You could also just ``append`` to ``self.tasks``,
        but this function call will also update the ``todotxt`` and
        ``linenr`` properties of ``task``.

        :param task: The task that should be added to this todo.txt file
        :type task: ``Task``
        """
        self.tasks.append(task)
        task.linenr = len(self.tasks)
        task.todotxt = self

    def parse(self):
        """(Re)parse ``self.filename``

        This will try to detect the line separator of the file automatically
        and remember it as ``self.linesep`` for the time when you save the
        file back to disk.

        :return: the list of all tasks read from the file.
        """
        self.tasks = []

        for task in self.parser.parse(pathlib.Path(self.filename)):
            task.todotxt = self
            self.tasks.append(task)

        self.linesep = self.parser.linesep
        return self.tasks

    def save(self, target=None, safe=True, linesep=None):
        """Save all tasks to disk

        If ``target`` is not provided, the ``filename`` property is being
        used as the target file to save to.

        If ``safe`` is set (the default), the file will first be written to
        a temporary file in the same folder as the target file and after the
        successful write to disk, it will be moved in place of ``target``.
        This can cause trouble though with folders that are synchronised to
        some cloud storage.

        With ``linesep`` you can specify the line seperator. If it is not set
        it defaults to the systems default line seperator (or the detected
        line separator, if the file has been parsed from disk first).

        :param target: The file to save to, or ``None`` to use ``self.filename``
        :param safe: Whether or not to save the file in a way that does not
                     destroy the previous file in case on errors.
        :param linesep: The line separator, or ``None`` to use ``self.linesep``
        """
        if target is None:
            target = self.filename
        else:
            target = pathlib.Path(target)

        if linesep is None:
            linesep = self.linesep

        if safe:
            tmpfile = tempfile.NamedTemporaryFile('wb',
                                                  buffering=0,
                                                  dir=self.filename.parent,
                                                  delete=False,
                                                  prefix=".tmp",
                                                  suffix="~")
            self.write_to_stream(tmpfile, linesep)
            tmpfile.close()

            os.replace(tmpfile.name, target)
            try:
                os.unlink(tmpfile.name)
            except OSError:
                pass
        else:
            with open(target, 'wb', buffering=0) as fd:
                self.write_to_stream(fd, linesep)

    def write_to_stream(self, stream, linesep=None):
        """Save all tasks, ordered by their line number, to the stream

        :param stream: an ``io.IOBase`` like stream that accepts bytes being
                       written to it.
        :param linesep: the line separator, or ``None`` to use ``self.linesep``
        """
        if linesep is None:
            linesep = self.linesep
        stream.write(bytes(linesep.join(self.lines), self.encoding))

    @property
    def lines(self):
        """Much like ``self.tasks``, but already sorted by linenr and converted to string"""
        lines = [(task.linenr if task.linenr is not None else len(self.tasks), str(task))
                 for task in self.tasks]
        lines.sort()
        return [line for _, line in lines]

    def __repr__(self):
        return f'{self.__class__.__name__}(filename="{self.filename}")'


class TodoTxtParser:
    """A parser for todo.txt-like formatted strings or files"""
    def __init__(self, encoding='utf-8', task_type=None):
        """Create a new todo.txt parser

        :param encoding: The encoding to assume for the parsing process
        :param task_type: A subclass of ``Task`` to use when parsing the tasks."""
        self.encoding = encoding
        self.task_type = task_type or Task

        self.linesep = os.linesep
        """The line separator. After running any of the parse functions, this
        property will be set to the line separator that was detected in the
        parsed object."""

    def parse(self, target):
        """Parse the given object

        The behaviour of the parser depends a bit on what you pass in.
        It might be a bit surprising, but if you pass in a ``str``, ``parse``
        will attempt to find tasks in that string.

        If you want to parse a file and pass the filename, wrap it in
        ``pathlib.Path`` first or use ``parse_file`` directly.

        When parsing is completed, you can query ``linesep`` to see what
        the line separator was.

        :param target: the object to parse
        :type target: ``pathlib.Path``, ``str``, ``bytes``, or any ``io.IOBase``.
        :return: a list of tasks found in ``target``
        """
        if isinstance(target, pathlib.Path):
            return self.parse_file(target)
        if isinstance(target, str):
            return self.parse_str(target)
        if isinstance(target, bytes):
            return self.parse_str(str(target, self.encoding))
        if isinstance(target, io.IOBase):
            return self.parse_stream(target)
        raise TypeError(f"Don't know how to parse {type(target).__name__}")

    def parse_str(self, text):
        """Parse tasks from the given text

        :param text: The string containing todo.txt-like tasks
        :return: a list of tasks found in ``text``
        """
        self.linesep = os.linesep

        # determine line separator
        for ch in ['\r\n', '\n', '\r']:
            if ch in text:
                self.linesep = ch
                break

        return [self.task_type(line, linenr)
                for linenr, line in enumerate(text.rstrip().split(self.linesep))]

    def parse_file(self, path):
        """Parse the content of the file at ``path``

        :param path: The file to parse
        :return: a list of tasks found in ``file``.
        """
        with open(path, 'rt', encoding=self.encoding) as fh:
            return self.parse_stream(fh)

    def parse_stream(self, stream):
        """Parse an io stream

        :param stream: an io stream to read and parse tasks from
        :return: a list of tasks found in ``stream``
        """
        # get the text from the stream
        blob = stream.read()
        if not isinstance(blob, str):
            blob = str(blob, self.encoding)

        return self.parse_str(blob)

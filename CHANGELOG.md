# Changelog

This file contains the changes made between released versions.

The format is based on [Keep a changelog](https://keepachangelog.com/) and the versioning tries to follow
[Semantic Versioning](https://semver.org).

## 3.0.0
### Breaking change
- `TodoTxt.add()` now actually sets the `Task.linenr` property is accordance to the documentation of `Task.linenr`, starting at `0` (thanks to Adam)
- `TodoTxt.save(target="...", safe=True)` will create the temporary file in the location of the target instead of the location of `self.filename` (which might be read-only or on a different filesystem than the target)

### Fixed
- License specification in `pyproject.toml` is now a proper SPDX identifier


## 2.0.0
### Changed
- Behaviour when encountering a `a:b:c` was changed to interprete this as key `a` with value `b:c` instead of `a:b` with value `c`
- Switched to `pyproject.toml`


## 1.5.0
### Fixed
- Blank lines in a `todo.txt` file are ignored (they used to create a completely empty `Task`)


## 1.4.3
### Fixed
- `Task.remove_attribute` used to remove everything after the first occurrence of a matching attribute name (thanks to [Gal](https://github.com/gal064))


## 1.4.2
### Fixed
- Saving an empty `TodoTxt` would result in a file with a single newline ([#9](https://github.com/vonshednob/pytodotxt/issues/9))


## 1.4.1
### Fixed
- Missing trailing line separator when serialising a `TodoTxt`

### Changed
- `TodoTxt.lines` calls `TodoTxt.build_lines`


## 1.4.0
### Fixed
- `Task` would add the completion date to its `str` representation of a completed task even if there was no creation date set

### Added
- `TodoTxtParser` to make the parsing of a `todo.txt` file extendable
- `TodoTxt.write_to_stream` to write to an io stream instead of to disk
- Documentation. Finally.


## 1.3.0
### Added
- `__repr__` for both `Task` and `TodoTxt` added (thanks to [Sean Breckenridge](https://github.com/seanbreckenridge))

## 1.2.1
### Fixed
- Fix crash when creating `Task()` without any line content

## 1.2.0
### Added
- Detection of line ending when loading todo.txt files ([#3](https://github.com/vonshednob/pytodotxt/issues/3), thanks to [chaotika](https://github.com/chaotika))
- Configurable line ending when saving todo.txt files (thanks to [chaotika](https://github.com/chaotika))

## 1.1.0
### Fixed
- A task that had no description used to crash pytodotxt when attempting to add an attribute (or a context or a project)

### Added
- `bare_description` function of `Task` to get the description without any properties or contexts/projects ([#2](https://github.com/vonshednob/pytodotxt/issues/2))

## 1.0.7
### Fixed
- Fixed `__getattr__` error (thanks to [sandervoerman](https://github.com/sandervoerman))

## 1.0.6
### Fixed
- Fixed regression when saving with "safe-save" option

## 1.0.5
### Fixed
- Bug when saving files on Windows with non-ansi characters in the path name

## 1.0.4
### Added
- TodoTxt can be configured for an encoding

## 1.0.3
### Added
- Caching attributes to prevent repeated reparsing
- Have a reference in a task to the file that it belongs to
- Convenient access to task’s attributes by task.attr_name, eg. task.attr_due
  for due date

## 1.0.2
### Fixed
- Bug fix when task consists only of a date

## 1.0.0
- Splitting package into the basic library and its user-facing packages


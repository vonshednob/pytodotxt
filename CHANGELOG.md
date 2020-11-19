# Changelog

This file contains the changes made between released versions.

The format is based on [Keep a changelog](https://keepachangelog.com/) and the versioning tries to follow
[Semantic Versioning](https://semver.org).

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


Changelog
=========

2.4.0
-----
 - added optional arguments support to engine getter
 - added PyAMS monitoring extension

2.3.3
-----
 - packaging issue

2.3.2
-----
 - updated task execution report output

2.3.1
-----
 - updated doctests

2.3.0
-----
 - added PyAMS_scheduler pipeline support for SQLAlchemy tasks
 - updated execution report format to Markdown

2.2.0
-----
 - added support for last PyAMS_scheduler (>= 2.5) package and attached task execution reports
 - added support for Python 3.12

2.1.0
-----
 - updated syntax of settings used for dynamic schemas names
 - added support for global schema name replacement using a single alias

2.0.3
-----
 - updated SQLAlchemy columns getter in test form
 - Sonar scanner version reset

2.0.2
-----
 - updated task scheduler interfaces

2.0.1
-----
 - updated modal forms title

2.0.0
-----
 - upgraded to Pyramid 2.0 and SQLAlchemy 2.0

1.4.1
-----
 - added support for Python 3.11
 - updated doctest

1.4.0
-----
 - allow usage of dynamic text formatters into scheduler SQL tasks

1.3.6
-----
 - use new status on scheduler task execution failure

1.3.5
-----
 - PyAMS_security interfaces refactoring
 - added support for Python 3.10

1.3.4
-----
 - handle session commit when query doesn't return any result
 - updated SQLAlchemy task add/edit forms editor size
 - added doctests

1.3.3
-----
 - use new context base add action

1.3.2
-----
 - renamed permission constant

1.3.1
-----
 - use IUniqueID adapter "oid" value instead of adapter when creating new engine
 - updated "back" link target in engines container view

1.3.0
-----
 - added SQLAlchemy connections manager label adapter
 - updated add and edit forms title
 - updated package include scan

1.2.3
-----
 - use IObjectLabel interface instead of ITableElementName

1.2.2
-----
 - updated forms AJAX renderers
 - Pylint cleanups

1.2.1
-----
 - added missing "context" argument to permission check
 - updated add menus registration for last release of PyAMS_zmi package

1.2.0
-----
 - added option to disable two-phases commit on any SQLALchemy engine
 - added Pyramid setting to manage connections management thread; this setting can also be used
   to disable this thread completely

1.1.0
-----
 - removed support for Python < 3.7

1.0.0
-----
 - initial release

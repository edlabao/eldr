
Overview
========
This application framework is a collection of python code that serves to
jumpstart the development and standardize the behavior of command-line tools.


Application Base Class
======================
The application base class, :class:`~eldr.app.App`, is a virtual base class that
must be inherited by an application in order to use the framework. It provides
some basic features useful to most command-line applications such as exception
handling at the outer most scope of the application to prevent an application
from abruptly exiting silently, best-effort exit codes, logging methods, and
support for commonly used command-line arguments.

It has one virtual method named :meth:`~eldr.app.App.main()` that must be
implemented. A minimalist application need only implement this one method to use
the framework. However, there are other virtual methods that can be implemented
and public methods that can be overloaded to enable developers to extend and
customize an application.


Mixins
======
Mixins provide additional functionality to an application through multiple
inheritance, which is how mixins are implemented in Python. Each mixin class
usually provides just a narrow feature set. The philosophy here is that
applications should not be bloated by code that is never going to be run.
Instead, an application should be able to selectively load just the
functionality it needs.

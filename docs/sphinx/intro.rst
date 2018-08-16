
Overview
========
ELDR is an application framework, that is to say, it's a collection of python
code that can help jumpstart the development of command-line tools and
applications providing the developer is willing to follow a few rules and
conventions to use the framework.

The framework itself is fairly straighforward to use. An application will
inherit from a base application class named :class:`~eldr.app.App` and implement
one required method (:meth:`~eldr.app.App.main()`). From there, the application
can optionally implement a number of other prescribed methods to set up and
customize itself. For example, an application that needs custom command-line
arguments will implement the :meth:`~eldr.app.App.add_arguments()` and
:meth:`~eldr.app.App.process_arguments()` methods.

A lot of simple applications will probably only ever need the
:class:`~eldr.app.App` class, but for some more complex applications, additional
features are provided through mixin classes.


Application Base Class
======================
The application base class, :class:`~eldr.app.App`, is a virtual base class that
must be inherited by an application in order to use the framework. It provides
some basic features useful to most command-line applications. This includes
exception handling to prevent an application from abruptly exiting, a
best-effort exit code, logging methods, and built-in command-line arguments to
set various parameters.

It has one virtual method named :meth:`~eldr.app.App.main()` that must be
implemented. A minimalist application need only implement this one method to use
the framework. However, there are other virtual methods that can be implemented
and public methods that can be overloaded that enable developers to further
customize an application.

Here's the obligatory starting example::

    from eldr.app import App

    class HelloWorldApp(App):
        def main(self):
            self.log.info("Hello, World!")
            raise RuntimeError("Aaand goodbye...")

    if __name__ == "__main__":
        app = HelloWorldApp()
        app.run()

When saved to file named hello_world.py and run, it will print something like
the following output to the terminal::

    2018-04-10 22:00:10,379 INFO ---------------------------------------------------------------
    2018-04-10 22:00:10,379 INFO STARTING hello_world.py
    2018-04-10 22:00:10,379 INFO Hello, World!
    2018-04-10 22:00:10,379 ERROR Unhandled exception: Aaand goodbye...
    2018-04-10 22:00:10,379 ERROR > Traceback (most recent call last):
    2018-04-10 22:00:10,379 ERROR >   File "/lib/python/eldr/app/__init__.py", line 218, in run
    2018-04-10 22:00:10,379 ERROR >     self.main()
    2018-04-10 22:00:10,379 ERROR >   File "./hello_world.py", line 5, in main
    2018-04-10 22:00:10,379 ERROR >     raise RuntimeError("Aaand goodbye...")
    2018-04-10 22:00:10,379 ERROR > RuntimeError: Aaand goodbye...
    2018-04-10 22:00:10,379 INFO FINISHED hello_world.py
    2018-04-10 22:00:10,379 INFO - Exit status: 1

It's an underwhelming example to be sure, but for a few lines of code, we get a
timestamped output format (even the stack trace is properly formatted) and
logged callouts for the start, finish and exit status of our applications. Plus
if you bring up the help text with `hello_world.py -h`, you'll see a handful of
options that were automatically added to our application.


Mixins
======
Mixins provide additional functionality to an application through multiple
inheritance with each mixin class usually providing just a narrow feature set.
The philosophy here is that applications should not be bloated by code that is
never going to be run. Instead, an application should be able to selectively
load just the functionality it needs.

For example, to write a cron application, we would use the CronMixin class.
Because the application will run non-interactively, we'll probably also want to
log its output to a log file. Such an application class could be defined like
so::

    from eldr.app import App
    from eldr.app.mixin.cron import CronMixin
    from eldr.app.mixin.logfile import LogfileMixin

    class HelloWorldApp(CronMixin, LogfileMixin, App):
        # Class definition follows...

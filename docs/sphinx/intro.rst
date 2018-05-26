
Overview
========
This application framework is a collection of python code that serves to
jumpstart the development of command-line tools.


Application Base Class
======================
The application base class, App, is a virtual base class that must be inherited
by an application in order to use the framework. It provides just the most basic
features useful to most command-line applications such as exception handling at
the outer most scope of the application, best-effort exit codes, methods for
logging to stdout, and support for command-line arguments to set the logging
level or silence the application altogether. It has one virtual method named
main() that must be implemented. This is the entrypoint for the application
subclass.

In addition to the mandatory main() method, there are other virtual methods that
may be optionally implemented. These provide hooks into the application that can
be used to do things such as adding custom command-line options or overriding
the default output logging format.


Mixins
======
Mixins provide additional functionality to an application.

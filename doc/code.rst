Project documentation
=====================

This section contains the documentation that has been automatically extracted from source files with the ``sphinx`` tool.

It will be divided into three sections, namely one for the application data model, one for the controller and a last
one for the GUI, which reflect the MVC architectural pattern that has been adopted in order to design the overall
application architecture.

Contents:

.. toctree::
    :maxdepth: 2

    model
    controller
    view

Main entry point
^^^^^^^^^^^^^^^^
The project main entry point is the module named ``src.main``, which is conventionally part of the application
controller but is placed at the top level alongside with the three above packages (``model``, ``view`` and
``controller``) for practicality reasons.
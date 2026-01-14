..
   SEE COPYRIGHT and LICENCE NOTICES: files README-COPYRIGHT-utf8.txt and
   README-LICENCE-utf8.txt at project source root.

.. |PROJECT_NAME|      replace:: p-pattern
.. |SHORT_DESCRIPTION| replace:: Parametric patterns/shapes definition and sampling

.. |PYPI_NAME_LITERAL| replace:: ``p-pattern``
.. |PYPI_PROJECT_URL|  replace:: https://pypi.org/project/p-pattern/
.. _PYPI_PROJECT_URL:  https://pypi.org/project/p-pattern/

.. |DOCUMENTATION_URL| replace:: https://src.koda.cnrs.fr/eric.debreuve/p-pattern/-/wikis/home
.. _DOCUMENTATION_URL: https://src.koda.cnrs.fr/eric.debreuve/p-pattern/-/wikis/home

.. |DEPENDENCIES_MANDATORY| replace:: logger_36, numpy, scikit-image, scipy
.. |DEPENDENCIES_OPTIONAL|  replace:: None



===================================
|PROJECT_NAME|: |SHORT_DESCRIPTION|
===================================



Documentation
=============

The documentation is available at |DOCUMENTATION_URL|_.



Installation
============

This project is published
on the `Python Package Index (PyPI) <https://pypi.org/>`_
at: |PYPI_PROJECT_URL|_.
It should be installable from Python distribution platforms or Integrated Development Environments (IDEs).
Otherwise, it can be installed from a command console using `pip <https://pip.pypa.io/>`_:

+--------------+-------------------------------------------------------+----------------------------------------------------------+
|              | For all users (after acquiring administrative rights) | For the current user (no administrative rights required) |
+==============+=======================================================+==========================================================+
| Installation | ``pip install`` |PYPI_NAME_LITERAL|                   | ``pip install --user`` |PYPI_NAME_LITERAL|               |
+--------------+-------------------------------------------------------+----------------------------------------------------------+
| Update       | ``pip install --upgrade`` |PYPI_NAME_LITERAL|         | ``pip install --user --upgrade`` |PYPI_NAME_LITERAL|     |
+--------------+-------------------------------------------------------+----------------------------------------------------------+



Dependencies
============

The development relies on several packages:

- Mandatory: |DEPENDENCIES_MANDATORY|
- Optional:  |DEPENDENCIES_OPTIONAL|

The mandatory dependencies, if any, are installed automatically by `pip <https://pip.pypa.io/>`_, if they are not already, as part of the installation of |PROJECT_NAME|.
Python distribution platforms or Integrated Development Environments (IDEs) should also take care of this.
The optional dependencies, if any, must be installed independently by following the related instructions, for added functionalities of |PROJECT_NAME|.



Acknowledgments
===============

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
.. image:: https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336
    :target: https://pycqa.github.io/isort/

The project is developed with `PyCharm Community <https://www.jetbrains.com/pycharm/>`_.

The code is formatted by `Black <https://github.com/psf/black/>`_, *The Uncompromising Code Formatter*.

The imports are ordered by `isort <https://github.com/timothycrosley/isort/>`_... *your imports, so you don't have to*.

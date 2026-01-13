========================
PyAMS file views package
========================

.. contents::


What is PyAMS?
==============

PyAMS (Pyramid Application Management Suite) is a small suite of packages written for applications
and content management with the Pyramid framework.

**PyAMS** is actually mainly used to manage web sites through content management applications (CMS,
see PyAMS_content package), but many features are generic and can be used inside any kind of web
application.

All PyAMS documentation is available on `ReadTheDocs <https://pyams.readthedocs.io>`_; source code
is available on `Gitlab <https://gitlab.com/pyams>`_ and pushed to `Github
<https://github.com/py-ams>`_. Doctests are available in the *doctests* source folder.


What is PyAMS file views?
=========================

PyAMS file is a package dedicated to files management, including images.

This package is adding views and content providers and a management interface to manage files and
images through dedicated forms widgets which are integrated into PyAMS_skin and PyAMS_zmi
packages (but using PyAMS_zmi is not a requirement).

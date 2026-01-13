========================
PyAMS file views package
========================

Introduction
------------

This package is composed of a set of utility functions, usable into any Pyramid application.

    >>> from pyramid.testing import setUp, tearDown
    >>> config = setUp(hook_zca=True)

    >>> from cornice import includeme as include_cornice
    >>> include_cornice(config)
    >>> from cornice_swagger import includeme as include_swagger
    >>> include_swagger(config)
    >>> from pyams_utils import includeme as include_utils
    >>> include_utils(config)
    >>> from pyams_skin import includeme as include_skin
    >>> include_skin(config)
    >>> from pyams_zmi import includeme as include_zmi
    >>> include_zmi(config)
    >>> from pyams_file_views import includeme as include_file
    >>> include_file(config)
    >>> from pyams_file_views import includeme as include_file_views
    >>> include_file_views(config)


    >>> tearDown()

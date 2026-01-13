===================
PyAMS_layer package
===================

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
<https://github.com/py-ams>`_.


What is PyAMS_layer?
====================

PyAMS_layer is adding the concept of 'skin layers' to Pyramid.

A layer is a marker interface which will be used to tag a Request object; this tagging will allow
you to register templates, views or pagelets for only specific layers.

Skins are global utilities which have a "layer" attribute; when a skin is associated with a
context, the request is marked during traversal with this layer (removing all other layers
interfaces).

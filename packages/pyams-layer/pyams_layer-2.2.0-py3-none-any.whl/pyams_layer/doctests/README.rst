
===================
PyAMS_layer package
===================

Introduction
------------

This package is composed of a set of utility functions, usable into any Pyramid application.
They allow to handle layers and skins: a layer is a marker interface which is used to tag a
request; a skin is a named utility which is referencing this interface, and which can be
"applied" on a context: when the context is traversed by the request, this interface is applied
on the request, removing other layers interfaces which could have been applied previously.

    >>> from pyramid.testing import setUp, tearDown, DummyRequest
    >>> config = setUp(hook_zca=True)
    >>> config.registry.settings['zodbconn.uri'] = 'memory://'

    >>> from pyams_utils.request import get_annotations
    >>> config.add_request_method(get_annotations, 'annotations', reify=True)

    >>> from pyramid_zodbconn import includeme as include_zodbconn
    >>> include_zodbconn(config)
    >>> from cornice import includeme as include_cornice
    >>> include_cornice(config)
    >>> from cornice_swagger import includeme as include_swagger
    >>> include_swagger(config)
    >>> from pyams_utils import includeme as include_utils
    >>> include_utils(config)
    >>> from pyams_site import includeme as include_site
    >>> include_site(config)
    >>> from pyams_security import includeme as include_security
    >>> include_security(config)
    >>> from pyams_layer import includeme as include_layer
    >>> include_layer(config)

    >>> from pyams_site.generations import upgrade_site
    >>> request = DummyRequest()
    >>> site = upgrade_site(request)
    Upgrading PyAMS timezone to generation 1...


Skinning a request
------------------

    >>> from pyams_layer.interfaces import ISkin, PYAMS_BASE_SKIN_NAME
    >>> from pyams_layer.skin import PyAMSSkin
    >>> config.registry.registerUtility(PyAMSSkin, provided=ISkin, name=PYAMS_BASE_SKIN_NAME)

    >>> from pyams_layer.skin import apply_skin
    >>> request = DummyRequest()

    >>> from zope.traversing.interfaces import BeforeTraverseEvent
    >>> from pyams_layer.skin import handle_root_skin
    >>> handle_root_skin(BeforeTraverseEvent(site, request))

    >>> from pyams_layer.skin import get_skin
    >>> skin = get_skin(request)
    >>> skin
    <class 'pyams_layer.skin.PyAMSSkin'>
    >>> skin.layer
    <InterfaceClass pyams_layer.interfaces.IPyAMSLayer>
    >>> skin.layer.providedBy(request)
    True


Skinning contents
-----------------

When a skin is applied on "skinnable" content, this skin is automatically applied to request
during traversal:

    >>> from zope.container.folder import Folder
    >>> from pyams_layer.skin import UserSkinnableContentMixin
    >>> class Content(UserSkinnableContentMixin, Folder):
    ...     """Skinnable content"""

    >>> root = Folder()
    >>> content = Content()
    >>> root['content'] = content
    >>> content.skin = PYAMS_BASE_SKIN_NAME
    Traceback (most recent call last):
    ...
    zope.schema._bootstrapinterfaces.ConstraintNotSatisfied: ('PyAMS base skin', 'skin')

In fact, "PyAMS base skin" is the default skin, we can only set custom skins inheriting from it:

    >>> from zope.interface import implementer
    >>> from pyams_layer.interfaces import IPyAMSUserLayer

    >>> class IMyCustomLayer(IPyAMSUserLayer):
    ...     """Custom skin layer"""

    >>> class MyCustomSkin:
    ...     label = "My custom skin"
    ...     layer = IMyCustomLayer

    >>> config.registry.registerUtility(MyCustomSkin, provided=ISkin, name=MyCustomSkin.label)

    >>> content.skin = MyCustomSkin.label
    >>> content.skin
    'My custom skin'
    >>> content.can_inherit_skin
    False
    >>> content.inherit_skin
    False
    >>> content.inherit_skin = True
    >>> content.inherit_skin
    False
    >>> content.skin_parent is content
    True
    >>> content.get_skin(request)
    <class 'pyams_layer.tests.test_utilsdocs.MyCustomSkin'>

The "no_inherit" attribute is the opposite of "inherit"; it is used in management interface:

    >>> content.override_skin
    True

    >>> from zope.traversing.interfaces import BeforeTraverseEvent
    >>> from pyams_layer.skin import handle_content_skin
    >>> request = DummyRequest()
    >>> handle_content_skin(BeforeTraverseEvent(content, request))
    >>> get_skin(request) is MyCustomSkin
    True

Let's try to create an inner content:

    >>> subcontent = Content()
    >>> content['subcontent'] = subcontent
    >>> subcontent.can_inherit_skin
    True
    >>> subcontent.inherit_skin
    False
    >>> subcontent.override_skin = False
    >>> subcontent.inherit_skin
    True
    >>> subcontent.override_skin
    False
    >>> subcontent.skin_parent is content
    True
    >>> subcontent.skin
    'My custom skin'
    >>> subcontent.get_skin(request)
    <class 'pyams_layer.tests.test_utilsdocs.MyCustomSkin'>

    >>> request = DummyRequest()
    >>> handle_content_skin(BeforeTraverseEvent(subcontent, request))
    >>> get_skin(request) is None
    True

Here, skin is None because as subcontent is inheriting skin from it's parent, skin should have
been applied during traversal of parent object:

    >>> request = DummyRequest()
    >>> handle_content_skin(BeforeTraverseEvent(content, request))
    >>> handle_content_skin(BeforeTraverseEvent(subcontent, request))
    >>> get_skin(request) is MyCustomSkin
    True


Skins vocabularies
------------------

Two vocabularies are available to select skins:

    >>> from pyams_layer.vocabulary import SkinsVocabulary, UserSkinsVocabulary
    >>> vocabulary = SkinsVocabulary()
    >>> len(vocabulary)
    2
    >>> sorted(vocabulary._terms.keys())
    ['My custom skin', 'PyAMS base skin']

    >>> vocabulary = UserSkinsVocabulary()
    >>> len(vocabulary)
    1
    >>> sorted(vocabulary._terms.keys())
    ['My custom skin']


Custom skin resources
---------------------

When applying a custom skin, you can also apply custom resources like CSS of Javascript files;
the *custom_stylesheet* attribute allows to define a custom CSS file:

    >>> content.container_class is None
    True
    >>> content.custom_stylesheet is None
    True
    >>> subcontent.custom_stylesheet is None
    True

    >>> content.container_class = 'container-fluid'
    >>> content.container_class
    'container-fluid'
    >>> content.custom_stylesheet = '''/* CSS file content */'''
    >>> subcontent.custom_stylesheet.data
    b'/* CSS file content */'

    >>> subcontent.inherit_skin = False
    >>> subcontent.container_class is None
    True
    >>> subcontent.custom_stylesheet is None
    True
    >>> subcontent.inherit_skin = True

The *editor_stylesheet* attribute allows to define a custom stylesheet which will available in
HTML editor:

    >>> content.editor_stylesheet is None
    True
    >>> subcontent.editor_stylesheet is None
    True

    >>> content.editor_stylesheet = '''/* CSS editor content */'''
    >>> subcontent.editor_stylesheet.data
    b'/* CSS editor content */'

    >>> subcontent.inherit_skin = False
    >>> subcontent.editor_stylesheet is None
    True
    >>> subcontent.inherit_skin = True

Finally, the *custom_script* attribute can store a custom Javascript file:

    >>> content.custom_script is None
    True
    >>> subcontent.custom_script is None
    True

    >>> content.custom_script = '''/* JS custom content */'''
    >>> subcontent.custom_script.data
    b'/* JS custom content */'

    >>> subcontent.inherit_skin = False
    >>> subcontent.custom_script is None
    True
    >>> subcontent.inherit_skin = True


You can get container class from a TALES extension called "container_class":

    >>> from pyams_layer.skin import SkinContainerClassTALESExtension
    >>> extension = SkinContainerClassTALESExtension(content, request, None)
    >>> extension.render()
    'container-fluid'


Automatic inclusion of Fanstatic resources
------------------------------------------

Custom resources will be included automatically into Fanstatic resources list; we have to create
a custom WSGI application to test this:

    >>> import webob
    >>> from fanstatic import Injector, get_needed
    >>> from fanstatic.core import set_resource_file_existence_checking

    >>> from pyams_utils.fanstatic import ResourceWithData
    >>> from pyams_utils.testing import library
    >>> set_resource_file_existence_checking(False)
    >>> x1 = ResourceWithData(library, 'a.js', data={'test-value': 'nested'})
    >>> set_resource_file_existence_checking(True)

The first step is to provide *global* resources for our skin:

    >>> from pyams_utils.adapter import ContextRequestViewAdapter
    >>> class MySkinResources(ContextRequestViewAdapter):
    ...     resources = (x1,)

    >>> from zope.interface import Interface
    >>> from pyams_layer.interfaces import IResources
    >>> config.registry.registerAdapter(MySkinResources,
    ...                                 (Interface, IMyCustomLayer, Interface),
    ...                                 provided=IResources)

    >>> from zope.interface import alsoProvides
    >>> from pyramid.interfaces import IRequest
    >>> from pyams_utils.interfaces.tales import ITALESExtension

    >>> def app(environ, start_response):
    ...     start_response('200 OK', [('Content-Type', 'text/html')])
    ...     needed = get_needed()
    ...     extension = config.registry.queryMultiAdapter((content, request, None),
    ...                                                   ITALESExtension,
    ...                                                   name='resources')
    ...     extension.render()
    ...     needed.set_base_url('http://example.com')
    ...     return [b'<html><head></head><body></body></html>']

    >>> from fanstatic import Injector
    >>> app = Injector(app)

    >>> from pyramid.request import Request
    >>> request = Request.blank('/')
    >>> request.context = content
    >>> request.registry = config.registry
    >>> alsoProvides(request, IRequest)
    >>> apply_skin(request, MyCustomSkin)

    >>> response = request.get_response(app)
    >>> print(response.body.decode())
    <html><head><script data-test-value="nested" type="text/javascript" src="http://example.com/fanstatic/foo/a.js"></script>
    <script type="text/javascript" src="http://localhost/content/++attr++custom_script?_=..."></script>
    <link rel="stylesheet" type="text/css" href="http://localhost/content/++attr++custom_stylesheet?_=..." /></head><body></body></html>



Tests cleanup:

    >>> tearDown()

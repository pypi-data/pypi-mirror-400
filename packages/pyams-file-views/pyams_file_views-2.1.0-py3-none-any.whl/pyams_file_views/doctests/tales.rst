Rendering pictures
------------------

"picture" is a PyAMS TALES extension which can be used to render a complete responsive "<picture >"
HTML tag including all responsive selections of a given image; for testing purposes, we have to
register Pyramid's renderer:

    >>> from pyramid.testing import setUp, tearDown, DummyRequest
    >>> import os, sys, tempfile
    >>> temp_dir = tempfile.mkdtemp()

    >>> config = setUp(hook_zca=True)
    >>> config.registry.settings['zodbconn.uri'] = 'file://{dir}/Data.fs?blobstorage_dir={dir}/blobs'.format(
    ...     dir=temp_dir)

    >>> import transaction
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
    >>> from pyams_i18n import includeme as include_i18n
    >>> include_i18n(config)
    >>> from pyams_catalog import includeme as include_catalog
    >>> include_catalog(config)
    >>> from pyams_file import includeme as include_file
    >>> include_file(config)
    >>> from pyams_file_views import includeme as include_file_views
    >>> include_file_views(config)

    >>> from pyams_site.generations import upgrade_site
    >>> request = DummyRequest()
    >>> app = upgrade_site(request)
    Upgrading PyAMS timezone to generation 1...
    Upgrading PyAMS I18n to generation 1...
    Upgrading PyAMS catalog to generation 1...
    Upgrading PyAMS file to generation 4...

    >>> from pyramid_chameleon import zpt
    >>> config.add_renderer('.pt', zpt.renderer_factory)

    >>> from zope.traversing.interfaces import BeforeTraverseEvent
    >>> from pyramid.threadlocal import manager
    >>> from pyams_utils.registry import handle_site_before_traverse
    >>> handle_site_before_traverse(BeforeTraverseEvent(app, request))
    >>> manager.push({'request': request, 'registry': config.registry})

    >>> from pyams_file.tests import MyContent
    >>> img_name = os.path.join(sys.modules['pyams_file.tests'].__path__[0], 'test_image.png')

    >>> content = MyContent()
    >>> app['content'] = content
    >>> with open(img_name, 'rb') as file:
    ...     content.img_data = file
    >>> transaction.commit()

    >>> img = content.img_data

    >>> from zope.interface import alsoProvides, Interface
    >>> from pyams_utils.interfaces.tales import ITALESExtension
    >>> from pyams_utils.adapter import ContextRequestAdapter
    >>> view = ContextRequestAdapter(app, request)
    >>> alsoProvides(view, Interface)
    >>> extension = config.registry.queryMultiAdapter((img, request, view), ITALESExtension, name='picture')
    >>> extension.render()
    '<picture>...<source media="(max-width: 575px)"...srcset="http://example.com/content/++attr++img_data/++thumb++xs:w576?_=..." />...<source media="(min-width: 576px) and (max-width: 767px)"...srcset="http://example.com/content/++attr++img_data/++thumb++sm:w768?_=..." />...<source media="(min-width: 768px) and (max-width: 991px)"...srcset="http://example.com/content/++attr++img_data/++thumb++md:w992?_=..." />...<source media="(min-width: 992px) and (max-width: 1199px)"...srcset="http://example.com/content/++attr++img_data/++thumb++lg:w1200?_=..." />...<source media="(min-width: 1200px)"...srcset="http://example.com/content/++attr++img_data/++thumb++xl:w1600?_=..." />...<!-- fallback image -->...<img style="max-width: 100%;" class=""... alt="" src="http://example.com/content/++attr++img_data/++thumb++md:w1200?_=..." />...</picture>\n'

You can also use a custom field to define picture selections and width for each device type:

    >>> from pyams_skin.interfaces.schema import BootstrapThumbnailSelection
    >>> from pyams_skin.schema import BootstrapThumbnailsSelectionField
    >>> class IMySelection(Interface):
    ...     thumb_selection = BootstrapThumbnailsSelectionField(
    ...         title="Images selection",
    ...         default_width=6,
    ...         change_width=False,
    ...         required=False)

    >>> from zope.schema.fieldproperty import FieldProperty
    >>> class MySelection:
    ...     thumb_selection = FieldProperty(IMySelection['thumb_selection'])

    >>> selection = MySelection()
    >>> thumb_selection = selection.thumb_selection
    >>> thumb_selection.keys()
    dict_keys(['xs', 'sm', 'md', 'lg', 'xl'])
    >>> thumb_selection['xs']
    <pyams_skin.interfaces.schema.BootstrapThumbnailSelection object at 0x...>

    >>> thumb_selection['xs'].selection = 'portrait'
    >>> thumb_selection['xs'].selection
    'portrait'
    >>> thumb_selection['xs'].cols = 12
    >>> thumb_selection['xs'].cols
    12

    >>> extension.render(selections=thumb_selection)
    '<picture>...<source media="(max-width: 575px)"...srcset="http://example.com/content/++attr++img_data/++thumb++portrait:w576?_=..." />...<source media="(min-width: 576px) and (max-width: 767px)"...srcset="http://example.com/content/++attr++img_data/++thumb++sm:w384?_=..." />...<source media="(min-width: 768px) and (max-width: 991px)"...srcset="http://example.com/content/++attr++img_data/++thumb++md:w496?_=..." />...<source media="(min-width: 992px) and (max-width: 1199px)"...srcset="http://example.com/content/++attr++img_data/++thumb++lg:w600?_=..." />...<source media="(min-width: 1200px)"...srcset="http://example.com/content/++attr++img_data/++thumb++xl:w800?_=..." />...<!-- fallback image -->...<img style="max-width: 100%;" class=""... alt="" src="http://example.com/content/++attr++img_data/++thumb++portrait:w600?_=..." />...</picture>\n'


"thumbnail" is another TALES extension, which is used to render an image thumbnail of a source
image:

    >>> extension = config.registry.queryMultiAdapter((img, request, view), ITALESExtension, name='thumbnail')
    >>> extension.render()
    '<img src="http://example.com/content/++attr++img_data?_=..." class="" alt="" />'


Tests cleanup:

    >>> from pyams_file.interfaces.thumbnail import IThumbnails
    >>> IThumbnails(img).clear_thumbnails()

    >>> from pyams_utils.registry import set_local_registry
    >>> set_local_registry(None)
    >>> manager.clear()
    >>> transaction.commit()

    >>> tearDown()

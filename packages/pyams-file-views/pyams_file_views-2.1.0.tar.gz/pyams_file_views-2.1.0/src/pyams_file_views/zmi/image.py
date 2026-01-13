#
# Copyright (c) 2015-2020 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_file_views.zmi.image module

This module defines actions and view used to manipulate (rotate and resize) images, but also
to make selections of specific ratios used for responsive rendering.
"""

from collections import OrderedDict

from pyramid.httpexceptions import HTTPForbidden
from pyramid.view import view_config
from transaction.interfaces import ITransactionManager
from zope.component import getAdapters, queryAdapter, queryMultiAdapter
from zope.interface import Interface, implementer
from zope.schema import Bool, Int
from zope.schema.fieldproperty import FieldProperty

from pyams_file.image import ThumbnailGeometry
from pyams_file.interfaces import IImageFile, IResponsiveImage
from pyams_file.interfaces.thumbnail import IThumbnailer, IThumbnails
from pyams_file_views.zmi import FileModifierAction, FileModifierFormMixin
from pyams_form.ajax import ajax_form_config
from pyams_form.browser.checkbox import SingleCheckBoxFieldWidget
from pyams_form.button import handler
from pyams_form.field import Fields
from pyams_form.form import EditForm
from pyams_form.interfaces import DISPLAY_MODE
from pyams_form.interfaces.form import IAJAXFormRenderer
from pyams_form.interfaces.widget import IFileWidget
from pyams_layer.interfaces import IPyAMSLayer
from pyams_pagelet.pagelet import pagelet_config
from pyams_security.interfaces import IViewContextPermissionChecker
from pyams_security.interfaces.base import VIEW_SYSTEM_PERMISSION
from pyams_skin.interfaces import BOOTSTRAP_DEVICES_ICONS
from pyams_skin.interfaces.viewlet import IContentPrefixViewletManager, \
    IContextActionsViewletManager, IHelpViewletManager
from pyams_skin.schema.button import CloseButton, SubmitButton
from pyams_skin.viewlet.actions import ContextAction
from pyams_skin.viewlet.help import AlertMessage
from pyams_template.template import template_config
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.date import get_timestamp
from pyams_utils.interfaces import ICacheKeyValue
from pyams_utils.url import absolute_url
from pyams_viewlet.viewlet import Viewlet, viewlet_config
from pyams_zmi.form import AdminModalDisplayForm, AdminModalEditForm
from pyams_zmi.helper.event import get_json_image_refresh_callback
from pyams_zmi.interfaces import IAdminLayer


__docformat__ = 'restructuredtext'

from pyams_file_views import _  # pylint: disable=ungrouped-imports


#
# Image preview
#

@pagelet_config(name='preview.html',
                context=IImageFile, layer=IPyAMSLayer,
                permission=VIEW_SYSTEM_PERMISSION)
class ImagePreviewForm(AdminModalDisplayForm):
    """Image preview"""

    subtitle = _("Image preview")
    legend = _("Image preview")
    modal_class = 'modal-auto'


@viewlet_config(name='image-preview',
                context=IImageFile, layer=IAdminLayer, view=ImagePreviewForm,
                manager=IContentPrefixViewletManager, weight=10)
@template_config(template='templates/image-preview.pt')
class ImagePreviewImage(Viewlet):
    """Image preview viewlet"""


#
# Image rotate
#

@viewlet_config(name='image-rotate.action', context=IImageFile, layer=IAdminLayer,
                view=IFileWidget, manager=IContextActionsViewletManager, weight=20)
class ImageRotateAction(FileModifierAction):
    """Image rotate action"""

    hint = _("Rotate image right")
    icon_class = 'fas fa-redo fa-rotate-90'

    def get_href(self):
        return 'MyAMS.ajax.getJSON?url={}'.format(
            absolute_url(self.context, self.request, 'rotate.json'))


@view_config(name='rotate.json', context=IImageFile, request_type=IPyAMSLayer,
             renderer='json', xhr=True)
def rotate_image(request):
    """Rotate context image to the right"""
    image = request.context
    permission_checker = queryMultiAdapter((image, request, None), IViewContextPermissionChecker)
    if permission_checker is not None:
        permission = permission_checker.edit_permission
        if not request.has_permission(permission, context=image):
            raise HTTPForbidden()
    IImageFile(image).rotate(-90)
    # commit transaction to save blobs!
    ITransactionManager(image).commit()  # pylint: disable=too-many-function-args
    # return modified image
    thumbnail = IThumbnails(image).get_thumbnail('128x128')  # pylint: disable=assignment-from-no-return
    return {
        'status': 'success',
        'message': request.localizer.translate(EditForm.success_message),
        'callbacks': [
            get_json_image_refresh_callback(thumbnail,
                                            'thumbnail_{}'.format(ICacheKeyValue(image)),
                                            request)
        ]
    }


#
# Image crop
#

@viewlet_config(name='image-crop.action', context=IImageFile, layer=IAdminLayer,
                view=IFileWidget, manager=IContextActionsViewletManager, weight=30)
class ImageCropAction(FileModifierAction):
    """Image crop action"""

    hint = _("Crop image")
    icon_class = 'fas fa-crop'

    href = 'image-crop.html'
    modal_target = True


class IImageCropFormButtons(Interface):
    """Image crop form buttons"""

    crop = SubmitButton(name='crop', title=_("Crop"))
    cancel = CloseButton(name='cancel', title=_("Cancel"))


@ajax_form_config(name='image-crop.html', context=IImageFile, layer=IPyAMSLayer)
class ImageCropForm(FileModifierFormMixin, AdminModalEditForm):
    """Image crop form"""

    subtitle = _("Crop image")
    legend = _("New image selection")

    prefix = 'crop_form.'

    fields = Fields(Interface)
    buttons_interface = IImageCropFormButtons
    has_border = True

    @handler(IImageCropFormButtons['crop'])
    def handle_crop(self, action):
        """Crop button handler"""
        if self.mode == DISPLAY_MODE:
            return
        image = IImageFile(self.context)
        image_size = image.get_image_size()  # pylint: disable=assignment-from-no-return
        params = self.request.params
        x1 = int(params.get('selection.x1', 0))  # pylint: disable=invalid-name
        y1 = int(params.get('selection.y1', 0))  # pylint: disable=invalid-name
        x2 = int(params.get('selection.x2', image_size[0]))  # pylint: disable=invalid-name
        y2 = int(params.get('selection.y2', image_size[1]))  # pylint: disable=invalid-name
        image.crop(x1, y1, x2, y2)
        self.finished_state.update({
            'action': action,
            'changes': image
        })


@viewlet_config(name='image-crop.help', context=IImageFile, layer=IAdminLayer,
                view=ImageCropForm, manager=IHelpViewletManager, weight=10)
class ImageCropFormHelp(AlertMessage):
    """Image crop form help"""

    status = 'warning'
    _message = _("You can use this form to crop an image.  \n"
                 "**Cropping an image will alter the original image, and reset all thumbnails "
                 "and adaptive selections!**")

    message_renderer = 'markdown'


@viewlet_config(name='image-crop.select', context=IImageFile, layer=IAdminLayer,
                view=ImageCropForm, manager=IContentPrefixViewletManager, weight=10)
@template_config(template='templates/image-crop.pt')
class ImageCropFormPrefix(Viewlet):
    """Image crop form prefix viewlet"""


@adapter_config(required=(IImageFile, IPyAMSLayer, ImageCropForm),
                provides=IAJAXFormRenderer)
class ImageCropFormAJAXRenderer(ContextRequestViewAdapter):
    """Image crop form AJAX renderer"""

    def render(self, changes):
        """AJAX crop form renderer"""
        # commit transaction to store blobs!!
        ITransactionManager(changes).commit()  # pylint: disable=too-many-function-args
        # get new thumbnail
        thumbnail = IThumbnails(changes).get_thumbnail('128x128')  # pylint: disable=assignment-from-no-return
        return {
            'status': 'success',
            'message': self.request.localizer.translate(self.view.success_message),
            'callbacks': [
                get_json_image_refresh_callback(thumbnail,
                                                'thumbnail_{}'.format(ICacheKeyValue(thumbnail)),
                                                self.request)
            ]
        }


#
# Image selections base views
#

class ImageSelectionAction(FileModifierAction):
    """Image selection action"""

    selection_name = None
    modal_target = True

    @property
    def icon_class(self):
        """Icon class getter"""
        return BOOTSTRAP_DEVICES_ICONS.get(self.selection_name)

    def get_href(self):
        """Action URL getter"""
        return absolute_url(self.context, self.request,
                            '{}-selection.html'.format(self.selection_name))

    @property
    def hint(self):
        """Action hint getter, including thumbnail"""
        image = self.context
        request = self.request
        thumbnailer = queryAdapter(image, IThumbnailer, name=self.selection_name)
        return '''<div>{}</div>
        <div class="py-2">
            <img src="{}/++thumb++{}:200x128?_={}" />
        </div>'''.format(request.localizer.translate(thumbnailer.label),
                         absolute_url(image, request),
                         self.selection_name,
                         get_timestamp(image))


class IImageSelectionFormButtons(Interface):
    """Image thumbnail form buttons"""

    select = SubmitButton(name='select', title=_("Select thumbnail"))
    cancel = CloseButton(name='close', title=_("Cancel"))


class ImageSelectionForm(FileModifierFormMixin, AdminModalEditForm):
    """Image thumbnail selection form"""

    @property
    def subtitle(self):
        """Form legend getter"""
        thumbnailer = queryAdapter(self.context, IThumbnailer, name=self.selection_name)
        if thumbnailer is not None:
            translate = self.request.localizer.translate
            return translate(_("{} selection")).format(translate(thumbnailer.label).lower())
        return None

    legend = _("Image selection")
    prefix = 'thumbnail_form.'

    fields = Fields(Interface)
    buttons_interface = IImageSelectionFormButtons

    has_border = True

    selection_name = None

    @property
    def selection_ratio(self):
        """Selection ratio getter"""
        thumbnailer = queryAdapter(self.context, IThumbnailer, name=self.selection_name)
        return '{0[0]}:{0[1]}'.format(thumbnailer.ratio) \
            if thumbnailer.ratio[0] is not None else None

    @handler(IImageSelectionFormButtons['select'])
    def handle_select(self, action):
        """Select button handler"""
        if self.mode == DISPLAY_MODE:
            return
        image = IImageFile(self.context)
        params = self.request.params
        geometry = ThumbnailGeometry()
        geometry.x1 = int(params.get('selection.x1'))
        geometry.y1 = int(params.get('selection.y1'))
        geometry.x2 = int(params.get('selection.x2'))
        geometry.y2 = int(params.get('selection.y2'))
        if not geometry.is_empty():
            IThumbnails(image).set_geometry(self.selection_name, geometry)
            self.finished_state.update({
                'action': action,
                'changes': image
            })


@viewlet_config(name='selection-form.prefix', context=IImageFile, layer=IAdminLayer,
                view=ImageSelectionForm, manager=IContentPrefixViewletManager, weight=10)
@template_config(template='templates/image-selection.pt')
class ImageSelectionFormPrefix(Viewlet):
    """Thumbnail form selection prefix"""


#
# Portrait selection form
#

@viewlet_config(name='portrait-selection.action', context=IImageFile, layer=IAdminLayer,
                view=IFileWidget, manager=IContextActionsViewletManager, weight=50)
class ImagePortraitSelectionAction(ImageSelectionAction):
    """Image portrait selection action"""

    selection_name = 'portrait'
    icon_class = 'fas fa-id-badge'


@ajax_form_config(name='portrait-selection.html', context=IImageFile, layer=IPyAMSLayer)
class ImagePortraitSelectionForm(ImageSelectionForm):
    """Image portrait selection form"""

    selection_name = 'portrait'


#
# Square selection form
#

@viewlet_config(name='square-selection.action', context=IImageFile, layer=IAdminLayer,
                view=IFileWidget, manager=IContextActionsViewletManager, weight=52)
class ImageSquareSelectionAction(ImageSelectionAction):
    """Image square selection action"""

    selection_name = 'square'
    icon_class = 'fab fa-instagram-square'


@ajax_form_config(name='square-selection.html', context=IImageFile, layer=IPyAMSLayer)
class ImageSquareSelectionForm(ImageSelectionForm):
    """Image square selection form"""

    selection_name = 'square'


#
# Panoramic selection form
#

@viewlet_config(name='pano-selection.action', context=IImageFile, layer=IAdminLayer,
                view=IFileWidget, manager=IContextActionsViewletManager, weight=54)
class ImagePanoSelectionAction(ImageSelectionAction):
    """Image panoramic selection action"""

    selection_name = 'pano'
    icon_class = 'fas fa-film'


@ajax_form_config(name='pano-selection.html', context=IImageFile, layer=IPyAMSLayer)
class ImagePanoSelectionForm(ImageSelectionForm):
    """Image panoramic selection form"""

    selection_name = 'pano'


#
# Card selection form
#

@viewlet_config(name='card-selection.action', context=IImageFile, layer=IAdminLayer,
                view=IFileWidget, manager=IContextActionsViewletManager, weight=56)
class ImageCardSelectionAction(ImageSelectionAction):
    """Image card selection action"""

    selection_name = 'card'
    icon_class = 'fa fa-address-card'


@ajax_form_config(name='card-selection.html', context=IImageFile, layer=IPyAMSLayer)
class ImageCardSelectionForm(ImageSelectionForm):
    """Image card selection form"""

    selection_name = 'card'


#
# Banner selection form
#

@viewlet_config(name='banner-selection.action', context=IImageFile, layer=IAdminLayer,
                view=IFileWidget, manager=IContextActionsViewletManager, weight=58)
class ImageBannerSelectionAction(ImageSelectionAction):
    """Image banner selection action"""

    selection_name = 'banner'
    icon_class = 'fas fa-window-minimize fa-rotate-180'


@ajax_form_config(name='banner-selection.html', context=IImageFile, layer=IPyAMSLayer)
class ImageBannerSelectionForm(ImageSelectionForm):
    """Image banner selection form"""

    selection_name = 'banner'


class ResponsiveImageSelectionForm(ImageSelectionForm):
    """Responsive image selection form"""

    selection_ratio = None


#
# XS responsive selection form
#

@viewlet_config(name='xs-selection.action', context=IResponsiveImage, layer=IAdminLayer,
                view=IFileWidget, manager=IContextActionsViewletManager, weight=60)
class ImageXSSelectionAction(ImageSelectionAction):
    """Image XS selection action"""

    selection_name = 'xs'


@ajax_form_config(name='xs-selection.html', context=IResponsiveImage, layer=IPyAMSLayer)
class ImageXSSelectionForm(ResponsiveImageSelectionForm):
    """Image XS selection form"""

    selection_name = 'xs'


#
# SM responsive selection form
#

@viewlet_config(name='sm-selection.action', context=IResponsiveImage, layer=IAdminLayer,
                view=IFileWidget, manager=IContextActionsViewletManager, weight=62)
class ImageSMSelectionAction(ImageSelectionAction):
    """Image SM selection action"""

    selection_name = 'sm'


@ajax_form_config(name='sm-selection.html', context=IResponsiveImage, layer=IPyAMSLayer)
class ImageSMSelectionForm(ImageSelectionForm):
    """Image SM selection form"""

    selection_name = 'sm'


#
# MD responsive selection form
#

@viewlet_config(name='md-selection.action', context=IResponsiveImage, layer=IAdminLayer,
                view=IFileWidget, manager=IContextActionsViewletManager, weight=64)
class ImageMDSelectionAction(ImageSelectionAction):
    """Image MD selection action"""

    selection_name = 'md'


@ajax_form_config(name='md-selection.html', context=IResponsiveImage, layer=IPyAMSLayer)
class ImageMDSelectionForm(ImageSelectionForm):
    """Image MD selection form"""

    selection_name = 'md'


#
# LG responsive selection form
#

@viewlet_config(name='lg-selection.action', context=IResponsiveImage, layer=IAdminLayer,
                view=IFileWidget, manager=IContextActionsViewletManager, weight=66)
class ImageLGSelectionAction(ImageSelectionAction):
    """Image LG selection action"""

    selection_name = 'lg'


@ajax_form_config(name='lg-selection.html', context=IResponsiveImage, layer=IPyAMSLayer)
class ImageLGSelectionForm(ImageSelectionForm):
    """Image LG selection form"""

    selection_name = 'lg'


#
# XL responsive selection form
#

@viewlet_config(name='xl-selection.action', context=IResponsiveImage, layer=IAdminLayer,
                view=IFileWidget, manager=IContextActionsViewletManager, weight=68)
class ImageXLSelectionAction(ImageSelectionAction):
    """Image XL selection action"""

    selection_name = 'xl'


@ajax_form_config(name='xl-selection.html', context=IResponsiveImage, layer=IPyAMSLayer)
class ImageXLSelectionForm(ImageSelectionForm):
    """Image XL selection form"""

    selection_name = 'xl'


#
# Complete selections display form
#

@viewlet_config(name='image-selections.action', context=IImageFile, layer=IAdminLayer,
                view=IFileWidget, manager=IContextActionsViewletManager, weight=100)
class ImageSelectionsAction(ContextAction):
    """Image selections action"""

    hint = _("Display all selections")
    icon_class = 'fas fa-th-large text-primary'
    href = 'image-selections.html'
    modal_target = True


@pagelet_config(name='image-selections.html', context=IImageFile, request_type=IPyAMSLayer)
class ImageSelectionsDisplayForm(AdminModalDisplayForm):
    """Image selections display form"""

    modal_class = 'modal-xl'

    subtitle = _("Display all image selections")
    legend = _("Current image selections")

    fields = Fields(Interface)


@viewlet_config(name='image-selections.prefix', context=IImageFile, layer=IAdminLayer,
                view=ImageSelectionsDisplayForm, manager=IContentPrefixViewletManager)
@template_config(template='templates/image-selections.pt')
class ImageSelectionsPrefix(Viewlet):
    """Image selections display form prefix"""

    def get_thumbnails(self):
        """Viewlet thumbnails getter"""
        thumbnails = IThumbnails(self.context)
        translate = self.request.localizer.translate
        result = OrderedDict()
        for name, adapter in sorted(getAdapters((self.context,), IThumbnailer),
                                    key=lambda x: x[1].weight):
            # pylint: disable=assignment-from-no-return
            thumbnail = thumbnails.get_thumbnail('{}{}200x128'.format(name, ':' if name else ''))
            result.setdefault(translate(adapter.section), []).append({
                'name': name,
                'label': translate(adapter.label),
                'thumbnail': thumbnail
            })
        return result


#
# Image resize
#

@viewlet_config(name='image-resize.action', context=IImageFile, layer=IAdminLayer,
                view=IFileWidget, manager=IContextActionsViewletManager, weight=150)
class ImageResizeAction(FileModifierAction):
    """Image resize action"""

    hint = _("Resize image")
    icon_class = 'fas fa-compress-alt'

    href = 'resize.html'
    modal_target = True


class IImageResizeInfo(Interface):
    """Image resize info interface"""

    width = Int(title=_("New image width"),
                min=1)

    height = Int(title=_("New image height"),
                 min=1)

    keep_ratio = Bool(title=_("Keep aspect ratio"),
                      description=_("Check to keep original image aspect ratio; image will then "
                                    "be resized as large as possible within given limits"),
                      required=True,
                      default=True)


@implementer(IImageResizeInfo)
class ImageResizeInfo:
    """Image resize info"""

    width = FieldProperty(IImageResizeInfo['width'])
    height = FieldProperty(IImageResizeInfo['height'])
    keep_ratio = FieldProperty(IImageResizeInfo['keep_ratio'])


@adapter_config(required=IImageFile, provides=IImageResizeInfo)
def image_resize_info_facttory(image):
    """Image resize info factory"""
    size = image.get_image_size()
    info = ImageResizeInfo()
    info.width = size[0]
    info.height = size[1]
    return info


class IImageResizeFormButtons(Interface):
    """Image resize form buttons"""

    resize = SubmitButton(name='resize', title=_("Resize image"))
    cancel = CloseButton(name='cancel', title=_("Cancel"))


@ajax_form_config(name='resize.html', context=IImageFile, layer=IPyAMSLayer)
class ImageResizeForm(FileModifierFormMixin, AdminModalEditForm):
    """Image resize form"""

    subtitle = _("Resize image")
    legend = _("New image size")

    fields = Fields(IImageResizeInfo)
    fields['keep_ratio'].widget_factory = SingleCheckBoxFieldWidget
    buttons_interface = IImageResizeFormButtons

    @handler(IImageResizeFormButtons['resize'])
    def handle_resize(self, action):
        """Resize button handler"""
        if self.mode == DISPLAY_MODE:
            return
        data, errors = self.extract_data()
        if errors:
            self.status = self.form_errors_message
            return
        IImageFile(self.context).resize(**data)
        self.finished_state.update({
            'action': action,
            'changes': self.context
        })


@viewlet_config(name='image-resize.help', context=IImageFile, layer=IAdminLayer,
                view=ImageResizeForm, manager=IHelpViewletManager, weight=10)
class ImageResizeFormHelp(AlertMessage):
    """Image resize form help"""

    status = 'warning'
    _message = _("You can use this form to reduce an image size.  \n"
                 "**Resizing an image will alter the original image, and reset all thumbnails "
                 "and adaptive selections!**")

    message_renderer = 'markdown'

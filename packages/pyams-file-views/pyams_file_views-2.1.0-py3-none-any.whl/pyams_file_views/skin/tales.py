#
# Copyright (c) 2015-2019 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_file.skin.tales module

This module provides several TALES extensions which can be used inside Chameleon templates.
"""

from pyramid.renderers import render
from zope.interface import Interface

from pyams_file.interfaces.thumbnail import IThumbnails
from pyams_file.skin import render_image
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.interfaces.tales import ITALESExtension


__docformat__ = 'restructuredtext'


@adapter_config(name='picture',
                required=(Interface, Interface, Interface),
                provides=ITALESExtension)
class PictureTALESExtension(ContextRequestViewAdapter):
    """Picture TALES adapter

    This TALES adapter can be used to automatically create a 'picture' HTML tag
    embedding all image attributes.
    """

    def render(self, context=None,
               xl_thumb='xl', xl_width=12, lg_thumb='lg', lg_width=12,
               md_thumb='md', md_width=12, sm_thumb='sm', sm_width=12,
               xs_thumb='xs', xs_width=12, def_thumb=None, def_width=None,
               alt='', css_class='', selections=None):
        # pylint: disable=too-many-arguments,too-many-locals
        """Render TALES extension"""
        if context is None:
            context = self.context
        if selections is not None:
            xl_thumb, xl_width = selections.get('xl').values
            lg_thumb, lg_width = selections.get('lg').values
            md_thumb, md_width = selections.get('md').values
            sm_thumb, sm_width = selections.get('sm').values
            xs_thumb, xs_width = selections.get('xs').values
        if context.content_type.startswith('image/svg'):
            return render('templates/svg-picture.pt', {
                'image': context,
                'xl_width': xl_width,
                'lg_width': lg_width,
                'md_width': md_width,
                'sm_width': sm_width,
                'xs_width': xs_width,
                'alt': alt,
                'css_class': css_class
            }, request=self.request)
        if def_thumb is None:
            def_thumb = md_thumb or lg_thumb or sm_thumb or xs_thumb or xl_thumb
        if def_width is None:
            def_width = md_width or lg_width or sm_width or xs_width or xl_width
        return render('templates/picture.pt', {
            'image': context,
            'xl_thumb': xl_thumb or 'xl',
            'xl_width': xl_width,
            'lg_thumb': lg_thumb or 'lg',
            'lg_width': lg_width,
            'md_thumb': md_thumb or 'md',
            'md_width': md_width,
            'sm_thumb': sm_thumb or 'sm',
            'sm_width': sm_width,
            'xs_thumb': xs_thumb or 'xs',
            'xs_width': xs_width,
            'def_thumb': def_thumb or 'md',
            'def_width': def_width,
            'alt': alt,
            'css_class': css_class
        }, request=self.request)


@adapter_config(name='thumbnails',
                required=(Interface, Interface, Interface),
                provides=ITALESExtension)
class ThumbnailsExtension(ContextRequestViewAdapter):
    """extension:thumbnails(image) TALES extension

    This TALES extension returns the IThumbnails adapter of given image.
    """

    def render(self, context=None):
        """Render TALES extension"""
        if context is None:
            context = self.context
        return IThumbnails(context, None)


@adapter_config(name='thumbnail',
                required=(Interface, Interface, Interface),
                provides=ITALESExtension)
class ThumbnailExtension(ContextRequestViewAdapter):
    """extension:thumbnail(image, width, height, css_class, img_class) TALES extension

    This TALES extension doesn't return an adapter but HTML code matching given image and
    dimensions. If image is a classic image, an "img" tag with source to thumbnail of required
    size is returned. If image in an SVG image, a "div" is returned containing whole SVG data of
    given image.
    """

    def render(self, context=None, width=None, height=None, css_class='', img_class='', alt=''):
        # pylint: disable=too-many-arguments
        """Render TALES extension"""
        if context is None:
            context = self.context
        return render_image(context, width, height, self.request, css_class, img_class, True, alt)

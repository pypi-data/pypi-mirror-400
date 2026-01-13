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

"""PyAMS_file_views.widget module

This module defines data converters and and form widgets which are required to manage files
and images.
"""

import os.path
from cgi import FieldStorage
from datetime import datetime, timezone

from pyramid.interfaces import IView
from zope.component import queryMultiAdapter
from zope.dublincore.interfaces import IZopeDublinCore
from zope.interface import implementer_only

from pyams_file.file import EXTENSIONS_THUMBNAILS
from pyams_file.interfaces.thumbnail import IThumbnails
from pyams_file.schema import IFileField, IMediaField
from pyams_form.browser.file import FileWidget as FileWidgetBase
from pyams_form.converter import BaseDataConverter
from pyams_form.interfaces import DISPLAY_MODE, IDataConverter, INPUT_MODE
from pyams_form.interfaces.widget import IFieldWidget, IFileWidget, IMediaFileWidget
from pyams_form.template import widget_template_config
from pyams_form.util import to_bytes
from pyams_form.widget import FieldWidget
from pyams_layer.interfaces import IPyAMSLayer
from pyams_utils.adapter import adapter_config
from pyams_utils.interfaces.form import NOT_CHANGED, TO_BE_DELETED
from pyams_utils.size import get_human_size
from pyams_utils.url import absolute_url


__docformat__ = 'restructuredtext'


@adapter_config(required=(IFileField, IFileWidget), provides=IDataConverter)
class FileUploadDataConverter(BaseDataConverter):
    """File upload data converter"""

    def to_widget_value(self, value):
        return value

    def to_field_value(self, value):
        deleted_field_name = '{}__deleted'.format(self.widget.name)
        deleted = self.widget.request.params.get(deleted_field_name)
        if deleted:
            return TO_BE_DELETED
        if (value is None) or (value is NOT_CHANGED) or (value == ''):
            return NOT_CHANGED
        if isinstance(value, FieldStorage):
            return value.filename, value.file
        if isinstance(value, tuple):
            return value
        return to_bytes(value)


@widget_template_config(mode=INPUT_MODE,
                        template='templates/file-input.pt', layer=IPyAMSLayer)
@widget_template_config(mode=DISPLAY_MODE,
                        template='templates/file-display.pt', layer=IPyAMSLayer)
@implementer_only(IFileWidget)
class FileWidget(FileWidgetBase):
    """File widget"""

    @property
    def timestamp(self):
        """Image timestamp getter"""
        dc = IZopeDublinCore(self.current_value, None)  # pylint: disable=invalid-name
        if dc is None:
            return datetime.now(timezone.utc).timestamp()
        return dc.modified.timestamp()  # pylint: disable=no-member

    @property
    def current_value(self):
        """Widget value getter"""
        if self.form.ignore_context:
            return None
        value = self.field.get(self.context)
        if isinstance(value, dict):
            lang = getattr(self, 'language', None)
            if lang is not None:
                value = value.get(lang)
        return value

    @property
    def deletable(self):
        """Widget deletable flag getter"""
        if self.required or self.field.required:
            return False
        if not self.ignore_context:
            value = self.current_value
        else:
            value = self.value
        return bool(value)

    def get_human_size(self):
        """File human size getter"""
        return get_human_size(self.current_value.get_size(), self.request)

    def get_thumbnail(self, geometry='128x128'):
        """File thumbnail getter"""
        thumbnails = IThumbnails(self.current_value, None)
        if thumbnails is not None:
            display = thumbnails.get_thumbnail(geometry)  # pylint: disable=assignment-from-no-return
            if display is not None:
                dc = IZopeDublinCore(display, None)  # pylint: disable=invalid-name
                if dc is None:
                    timestamp = self.timestamp
                else:
                    timestamp = dc.modified.timestamp()  # pylint: disable=no-member
                return '{}?_={}'.format(absolute_url(display, self.request),
                                        timestamp)
        filename = self.current_value.filename
        if filename:
            _name, ext = os.path.splitext(filename)
        else:
            ext = None
        return '/--static--/pyams_file/img/{}'.format(
            EXTENSIONS_THUMBNAILS.get(ext, 'unknown.png'))

    def get_thumbnail_target(self):
        """Widget thumbnail target getter"""
        value = self.current_value
        if value is not None:
            view = queryMultiAdapter((value, self.request), IView, name='preview.html')
            if view is not None:
                return absolute_url(value, self.request, 'preview.html')
        return None


@adapter_config(required=(IFileField, IPyAMSLayer), provides=IFieldWidget)
def FileFieldWidget(field, request):  # pylint: disable=invalid-name
    """File field widget factory"""
    return FieldWidget(field, FileWidget(request))


#
# Medias files widget
#

@widget_template_config(mode=INPUT_MODE,
                        template='templates/media-input.pt', layer=IPyAMSLayer)
@widget_template_config(mode=DISPLAY_MODE,
                        template='templates/media-display.pt', layer=IPyAMSLayer)
@implementer_only(IMediaFileWidget)
class MediaFileWidget(FileWidget):
    """Media file widget"""


@adapter_config(required=(IMediaField, IPyAMSLayer), provides=IFieldWidget)
def MediaFileFieldWidget(field, request):  # pylint: disable=invalid-name
    """Media file field widget factory"""
    return FieldWidget(field, MediaFileWidget(request))

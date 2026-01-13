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

"""PyAMS_file_views.zmi.file module

This module defines an action and a view to edit base files properties.
"""

from pyams_file.interfaces import IFile, IFileInfo
from pyams_form.ajax import ajax_form_config
from pyams_form.field import Fields
from pyams_form.interfaces.widget import IFileWidget, IWidget
from pyams_layer.interfaces import IPyAMSLayer
from pyams_security.interfaces.base import MANAGE_SYSTEM_PERMISSION
from pyams_skin.interfaces.view import IModalPage
from pyams_skin.interfaces.viewlet import IContextActionsViewletManager
from pyams_skin.viewlet.actions import ContextAction
from pyams_utils.adapter import adapter_config
from pyams_utils.date import get_timestamp
from pyams_utils.url import absolute_url
from pyams_viewlet.viewlet import viewlet_config
from pyams_zmi.form import AdminModalEditForm
from pyams_zmi.interfaces import IAdminLayer, IObjectLabel
from pyams_zmi.interfaces.form import IFormTitle


__docformat__ = 'restructuredtext'

from pyams_file_views import _  # pylint: disable=ungrouped-imports


@adapter_config(required=IFile,
                provides=IObjectLabel)
def file_label(context):
    """File label getter"""
    info = IFileInfo(context)
    return info.title or info.filename


@adapter_config(required=(IFile, IAdminLayer, IModalPage),
                provides=IFormTitle)
def file_modal_form_title(context, request, form):
    """File modal form title"""
    return context.title or context.filename


@viewlet_config(name='file-properties.action',
                context=IFile, layer=IPyAMSLayer, view=IFileWidget,
                manager=IContextActionsViewletManager, weight=10,
                permission=MANAGE_SYSTEM_PERMISSION)
class FilePropertiesAction(ContextAction):
    """File properties action"""

    hint = _("File properties")
    icon_class = 'far fa-edit'

    href = 'properties.html'
    modal_target = True


@ajax_form_config(name='properties.html',
                  context=IFile, layer=IPyAMSLayer,
                  permission=MANAGE_SYSTEM_PERMISSION)
class FilePropertiesEditForm(AdminModalEditForm):
    """File properties edit form"""

    subtitle = _("File properties")
    legend = _("Main file properties")

    fields = Fields(IFileInfo)


@viewlet_config(name='file-download.action',
                context=IFile, layer=IPyAMSLayer, view=IWidget,
                manager=IContextActionsViewletManager, weight=999)
class FileDownloadAction(ContextAction):
    """File download action"""

    label = _("Download")
    hint = _("Download original file")

    status = 'primary'
    target = 'download_window'

    def get_href(self):
        timestamp = get_timestamp(self.context)
        return '{}?dl=1&_={}'.format(absolute_url(self.context, self.request), timestamp)

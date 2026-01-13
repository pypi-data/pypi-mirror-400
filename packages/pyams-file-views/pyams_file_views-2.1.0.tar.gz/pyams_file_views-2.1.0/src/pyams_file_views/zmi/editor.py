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

"""PyAMS_file_views.zmi.editor module

This module defines an "editor" action and an associated view which allows to edit text
file contents with a rich text editor.
"""

from zope.interface import Interface, alsoProvides

from pyams_file.interfaces import IFile
from pyams_file_views.zmi import FileModifierAction
from pyams_form.ajax import ajax_form_config
from pyams_form.browser.textarea import TextAreaFieldWidget
from pyams_form.field import Fields
from pyams_layer.interfaces import IPyAMSLayer
from pyams_skin.interfaces.viewlet import IContextActionsViewletManager
from pyams_utils.interfaces.data import IObjectData
from pyams_viewlet.viewlet import viewlet_config
from pyams_zmi.form import AdminModalEditForm
from pyams_zmi.interfaces import IAdminLayer

__docformat__ = 'restructuredtext'

from pyams_file_views import _    # pylint: disable=ungrouped-imports


@viewlet_config(name='file-editor.action',
                context=IFile, layer=IAdminLayer, view=Interface,
                manager=IContextActionsViewletManager, weight=15)
class FileEditorAction(FileModifierAction):
    """File editor action"""

    def __new__(cls, context, request, view, manager):  # pylint: disable=unused-argument
        if context.content_type and \
                (context.content_type.startswith('text/') or
                 context.content_type.startswith('image/svg')):
            return FileModifierAction.__new__(cls)
        return None

    hint = _("Edit file content")
    icon_class = 'fa fa-file-alt'

    href = 'file-editor.html'
    modal_target = True


@ajax_form_config(name='file-editor.html',
                  context=IFile, layer=IPyAMSLayer)
class FileEditorForm(AdminModalEditForm):
    """File editor form"""

    subtitle = _("File content")
    legend = _("File content editor")

    prefix = 'editor_form.'
    modal_class = 'modal-xl'

    fields = Fields(IFile).select('data')
    fields['data'].widget_factory = TextAreaFieldWidget

    label_css_class = 'hidden'
    input_css_class = 'col-12'

    def update_widgets(self, prefix=None):
        super(FileEditorForm, self).update_widgets(prefix)
        if 'data' in self.widgets:
            widget = self.widgets['data']
            widget.add_class('height-100')
            widget.widget_css_class = "editor height-400px"
            widget.object_data = {
                'ams-filename': self.context.filename
            }
            alsoProvides(widget, IObjectData)

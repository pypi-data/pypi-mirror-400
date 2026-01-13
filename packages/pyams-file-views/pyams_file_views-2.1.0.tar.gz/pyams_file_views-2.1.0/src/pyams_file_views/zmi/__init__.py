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

"""PyAMS_file_views.zmi base module

This module defines a small set of base classes which are used by files management
interfaces, but also a file form permission checker which is used to extract edit permission
from context to which a file is attached to.
"""

from pyramid.location import lineage
from zope.component import queryAdapter, queryMultiAdapter
from zope.interface import Interface

from pyams_file.interfaces import IFile
from pyams_form.button import Buttons
from pyams_form.interfaces import DISPLAY_MODE
from pyams_security.interfaces import IViewContextPermissionChecker
from pyams_security.interfaces.base import FORBIDDEN_PERMISSION, MANAGE_PERMISSION
from pyams_skin.viewlet.actions import ContextAction
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_zmi.interfaces.form import IModalDisplayFormButtons


__docformat__ = 'restructuredtext'


class FileModifierAction(ContextAction):
    """File modifier action"""

    hint_placement = 'left'

    @property
    def permission(self):
        """Action permission getter"""
        try:
            return self.view.form.edit_permission
        except AttributeError:
            return MANAGE_PERMISSION


class FileModifierFormMixin:
    """Image modifier form mixin"""

    buttons_interface = IModalDisplayFormButtons

    @property
    def buttons(self):
        """Form buttons getter"""
        if self.mode == DISPLAY_MODE:
            return Buttons(IModalDisplayFormButtons)
        return Buttons(self.buttons_interface)


@adapter_config(required=(IFile, Interface, Interface),
                provides=IViewContextPermissionChecker)
class FileFormPermissionChecker(ContextRequestViewAdapter):
    """File form permission check"""

    @property
    def edit_permission(self):
        """File edit permission getter"""
        for parent in lineage(self.context.__parent__):
            checker = queryMultiAdapter((parent, self.request, self.view),
                                        IViewContextPermissionChecker)
            if checker is None:
                checker = queryAdapter(parent, IViewContextPermissionChecker)
            if checker is not None:
                return checker.edit_permission
        return FORBIDDEN_PERMISSION

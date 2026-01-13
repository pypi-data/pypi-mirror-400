# -*- coding: utf-8; -*-
################################################################################
#
#  WuttaSync -- Wutta Framework for data import/export and real-time sync
#  Copyright © 2024-2026 Lance Edgar
#
#  This file is part of Wutta Framework.
#
#  Wutta Framework is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option) any
#  later version.
#
#  Wutta Framework is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  Wutta Framework.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Export Handlers
"""

from wuttasync.importing import ImportHandler, Orientation


class ExportHandler(ImportHandler):
    """
    Generic base class for :term:`export handlers <import handler>`.

    This is really just
    :class:`~wuttasync.importing.handlers.ImportHandler` with the
    orientation flipped.
    """

    orientation = Orientation.EXPORT
    ""  # nb. suppress docs


class ToFileHandler(ExportHandler):
    """
    Base class for export handlers which use output file(s) as the
    data target.

    Importers (exporters) used by this handler are generally assumed
    to subclass :class:`~wuttasync.exporting.base.ToFile`.
    """

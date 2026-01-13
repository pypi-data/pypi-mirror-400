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
Data exporter base classes
"""

import os

from wuttasync.importing import Importer


class ToFile(Importer):
    """
    Base class for importer/exporter using output file as data target.

    Depending on the subclass, it may be able to "guess" (at least
    partially) the path to the output file.  If not, and/or to avoid
    ambiguity, the caller must specify the file path.

    In most cases caller may specify any of these via kwarg to the
    class constructor, or e.g.
    :meth:`~wuttasync.importing.handlers.ImportHandler.process_data()`:

    * :attr:`output_file_path`
    * :attr:`output_file_name`

    The subclass itself can also specify via override of these
    methods:

    * :meth:`get_output_file_path()`
    * :meth:`get_output_file_name()`

    And of course subclass must override these too:

    * :meth:`open_output_file()`
    * :meth:`close_output_file()`
    * (and see also :attr:`output_file`)
    """

    output_file_path = None
    """
    Path to output folder, or file.

    The ideal usage is to set this to the output *folder* path.  That
    allows the handler to run several importers in one go.  The same
    output folder path is given to each importer; they then each
    determine their own output filename within that.

    But you can also set this to the full output folder + file path,
    e.g. if you're just running one importer.  This would override
    the importer's own logic for determining output filename.

    See also :meth:`get_output_file_path()` and
    :meth:`get_output_file_name()`.
    """

    output_file_name = None
    """
    Optional static output file name (sans folder path).

    If set, this will be used as output filename instead of the
    importer determining one on its own.

    See also :meth:`get_output_file_name()`.
    """

    output_file = None
    """
    Handle to the open output file, if applicable.  May be set by
    :meth:`open_output_file()` for later reference within
    :meth:`close_output_file()`.
    """

    def setup(self):
        """
        Open the output file.  See also :meth:`open_output_file()`.
        """
        if not self.dry_run:
            self.open_output_file()

    def teardown(self):
        """
        Close the output file.  See also :meth:`close_output_file()`.
        """
        if not self.dry_run:
            self.close_output_file()

    def get_output_file_path(self):
        """
        This must return the full path to output file.

        Default logic inspects :attr:`output_file_path`; if that
        points to a folder then it is combined with
        :meth:`get_output_file_name()`.  Otherwise it's returned
        as-is.

        :returns: Path to output file, as string
        """
        path = self.output_file_path
        if not path:
            raise ValueError("must set output_file_path")

        if os.path.isdir(path):
            filename = self.get_output_file_name()
            return os.path.join(path, filename)

        return path

    def get_output_file_name(self):
        """
        This must return the output filename, sans folder path.

        Default logic will return :attr:`output_file_name` if set,
        otherwise raise error.

        :returns: Output filename, sans folder path
        """
        if self.output_file_name:
            return self.output_file_name

        raise NotImplementedError("can't guess output filename")

    def open_output_file(self):
        """
        Open the output file for writing target data.

        Subclass must override to specify how this happens; default
        logic is not implemented.  Remember to set :attr:`output_file`
        if applicable for reference when closing.

        See also :attr:`get_output_file_path()` and
        :meth:`close_output_file()`.
        """
        raise NotImplementedError

    def close_output_file(self):
        """
        Close the output file for target data.

        Subclass must override to specify how this happens; default
        logic blindly calls the ``close()`` method on whatever
        :attr:`output_file` happens to point to.

        See also :attr:`open_output_file()`.
        """
        self.output_file.close()

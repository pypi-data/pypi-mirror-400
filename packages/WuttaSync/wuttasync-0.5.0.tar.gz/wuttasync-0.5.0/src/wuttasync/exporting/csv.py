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
Exporting to CSV
"""

import csv
import logging
from collections import OrderedDict

import sqlalchemy as sa
from sqlalchemy_utils.functions import get_primary_keys, get_columns

from wuttjamaican.db.util import make_topo_sortkey

from wuttasync.importing import FromWuttaHandler, FromWutta
from wuttasync.exporting import ToFileHandler, ToFile


log = logging.getLogger(__name__)


class ToCsv(ToFile):  # pylint: disable=abstract-method
    """
    Base class for exporter using CSV file as data target.

    This inherits from :class:`~wuttasync.exporting.base.ToFile`.
    """

    output_writer = None
    """
    While the output file is open, this will reference a
    :class:`python:csv.DictWriter` instance.
    """

    csv_encoding = "utf_8"
    """
    Encoding used for the CSV output file.

    You can specify an override if needed when calling
    :meth:`~wuttasync.importing.handlers.ImportHandler.process_data()`.
    """

    def get_output_file_name(self):  # pylint: disable=empty-docstring
        """ """
        if self.output_file_name:
            return self.output_file_name

        model_title = self.get_model_title()
        return f"{model_title}.csv"

    def open_output_file(self):
        """
        Opens the output CSV file for writing.

        This calls
        :meth:`~wuttasync.exporting.base.ToFile.get_output_file_path()`
        and opens that file.  It sets
        :attr:`~wuttasync.exporting.base.ToFile.output_file` and also
        :attr:`output_writer`.  And it calls
        :meth:`write_output_header()` to write the field header row.
        """
        path = self.get_output_file_path()
        log.debug("opening output file: %s", path)

        self.output_file = open(  # pylint: disable=consider-using-with
            path, "wt", encoding=self.csv_encoding
        )

        self.output_writer = csv.DictWriter(
            self.output_file,
            self.fields,
            # quoting=csv.QUOTE_NONNUMERIC
        )

        self.write_output_header()

    def write_output_header(self):
        """
        Write the field header row to the CSV file.

        Default logic calls
        :meth:`~python:csv.DictWriter.writeheader()` on the
        :attr:`output_writer` instance.
        """
        self.output_writer.writeheader()

    def close_output_file(self):  # pylint: disable=empty-docstring
        """ """
        self.output_writer = None
        self.output_file.close()
        self.output_file = None

    def update_target_object(self, obj, source_data, target_data=None):
        """
        In a CSV export the assumption is we always start with an
        empty file, so "create" is the only logical action for each
        record - there are no updates or deletes per se.

        But under the hood, this method is used for create as well, so
        we override it and actually write the record to CSV file.
        Unless :attr:`~wuttasync.importing.base.Importer.dry_run` is
        true, this calls :meth:`~python:csv.csvwriter.writerow()` on
        the :attr:`output_writer` instance.

        See also parent method docs,
        :meth:`~wuttasync.importing.base.Importer.update_target_object()`
        """
        data = self.coerce_csv(source_data)
        if not self.dry_run:
            self.output_writer.writerow(data)
        return data

    def coerce_csv(self, data):  # pylint: disable=missing-function-docstring
        coerced = {}
        for field in self.fields:
            value = data[field]

            if value is None:
                value = ""

            elif isinstance(value, (int, float)):
                pass

            else:
                value = str(value)

            coerced[field] = value
        return coerced


class FromSqlalchemyToCsvMixin:
    """
    Mixin class for SQLAlchemy ORM → CSV :term:`exporters <importer>`.

    Such exporters are generated automatically by
    :class:`FromSqlalchemyToCsvHandlerMixin`, so you won't typically
    reference this mixin class directly.

    This mixin effectively behaves like the
    :attr:`~wuttasync.importing.base.Importer.model_class` represents
    the source side instead of the target.  It uses
    :attr:`~wuttasync.importing.base.FromSqlalchemy.source_model_class`
    instead, for automatic things like inspecting the fields list.
    """

    def get_model_title(self):  # pylint: disable=missing-function-docstring
        if hasattr(self, "model_title"):
            return self.model_title
        return self.source_model_class.__name__

    def get_simple_fields(self):  # pylint: disable=missing-function-docstring
        if hasattr(self, "simple_fields"):
            return self.simple_fields
        try:
            fields = get_columns(self.source_model_class)
        except sa.exc.NoInspectionAvailable:
            return []
        return list(fields.keys())

    def normalize_source_object(
        self, obj
    ):  # pylint: disable=missing-function-docstring
        fields = self.get_fields()
        fields = [f for f in self.get_simple_fields() if f in fields]
        data = {field: getattr(obj, field) for field in fields}
        return data

    def make_object(self):  # pylint: disable=missing-function-docstring
        return self.source_model_class()


class FromSqlalchemyToCsvHandlerMixin:
    """
    Mixin class for SQLAlchemy ORM → CSV :term:`export handlers
    <import handler>`.

    This knows how to dynamically generate :term:`exporter <importer>`
    classes to represent the models in the source ORM.  Such classes
    will inherit from :class:`FromSqlalchemyToCsvMixin`, in addition
    to whatever :attr:`FromImporterBase` and :attr:`ToImporterBase`
    reference.

    That all happens within :meth:`define_importers()`.
    """

    target_key = "csv"
    generic_target_title = "CSV"

    # nb. subclass must define this
    FromImporterBase = None
    """
    For a handler to use this mixin, it must set this to a valid base
    class for the ORM source side.  The :meth:`define_importers()`
    logic will use this when dynamically generating new exporter
    classes.
    """

    ToImporterBase = ToCsv
    """
    This must be set to a valid base class for the CSV target side.
    Default is :class:`ToCsv` which should typically be fine; you can
    change if needed.
    """

    def get_source_model(self):
        """
        This should return the :term:`app model` or a similar module
        containing data model classes for the source side.

        The source model is used to dynamically generate a set of
        exporters (e.g. one per table in the source DB) which can use
        CSV file as data target.  See also :meth:`define_importers()`.

        Subclass must override this if needed; default behavior is not
        implemented.
        """
        raise NotImplementedError

    def define_importers(self):
        """
        This mixin overrides typical (manual) importer definition, and
        instead dynamically generates a set of exporters, e.g. one per
        table in the source DB.

        It does this based on the source model, as returned by
        :meth:`get_source_model()`.  It calls
        :meth:`make_importer_factory()` for each model class found.
        """
        importers = {}
        model = self.get_source_model()

        # mostly try to make an importer for every data model
        for name in dir(model):
            cls = getattr(model, name)
            if (
                isinstance(cls, type)
                and issubclass(cls, model.Base)
                and cls is not model.Base
            ):
                importers[name] = self.make_importer_factory(cls, name)

        # sort importers according to schema topography
        topo_sortkey = make_topo_sortkey(model)
        importers = OrderedDict(
            [(name, importers[name]) for name in sorted(importers, key=topo_sortkey)]
        )

        return importers

    def make_importer_factory(self, model_class, name):
        """
        Generate a new :term:`exporter <importer>` class, targeting
        the given :term:`data model` class.

        The newly-created class will inherit from:

        * :class:`FromSqlalchemyToCsvMixin`
        * :attr:`FromImporterBase`
        * :attr:`ToImporterBase`

        :param model_class: A data model class.

        :param name: The "model name" for the importer/exporter.  New
           class name will be based on this, so e.g. ``Widget`` model
           name becomes ``WidgetImporter`` class name.

        :returns: The new class, meant to process import/export
           targeting the given data model.
        """
        return type(
            f"{name}Importer",
            (FromSqlalchemyToCsvMixin, self.FromImporterBase, self.ToImporterBase),
            {
                "source_model_class": model_class,
                "default_keys": list(get_primary_keys(model_class)),
            },
        )


class ToCsvHandler(ToFileHandler):
    """
    Base class for export handlers using CSV file(s) as data target.
    """


class FromWuttaToCsv(
    FromSqlalchemyToCsvHandlerMixin, FromWuttaHandler, ToCsvHandler
):  # pylint: disable=too-many-ancestors
    """
    Handler for Wutta (:term:`app database`) → CSV export.

    This uses :class:`FromSqlalchemyToCsvHandlerMixin` for most of the
    heavy lifting.
    """

    FromImporterBase = FromWutta

    def get_source_model(self):  # pylint: disable=empty-docstring
        """ """
        return self.app.model

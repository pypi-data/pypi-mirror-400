# -*- coding: utf-8; -*-

import csv
import io
from unittest.mock import patch

from wuttjamaican.testing import DataTestCase

from wuttasync.exporting import csv as mod, ExportHandler
from wuttasync.importing import FromWuttaHandler, FromWutta


class TestToCsv(DataTestCase):

    def setUp(self):
        self.setup_db()
        self.handler = ExportHandler(self.config)

    def make_exporter(self, **kwargs):
        kwargs.setdefault("handler", self.handler)
        kwargs.setdefault("output_file_path", self.tempdir)
        return mod.ToCsv(self.config, **kwargs)

    def test_get_output_file_name(self):
        model = self.app.model
        exp = self.make_exporter(model_class=model.Setting)

        # name can be guessed
        self.assertEqual(exp.get_output_file_name(), "Setting.csv")

        # name can be explicitly set
        exp.output_file_name = "data.txt"
        self.assertEqual(exp.get_output_file_name(), "data.txt")

    def test_open_output_file(self):
        model = self.app.model
        exp = self.make_exporter(model_class=model.Setting)
        self.assertIsNone(exp.output_file)
        self.assertIsNone(exp.output_writer)
        exp.open_output_file()
        try:
            self.assertIsInstance(exp.output_file, io.TextIOBase)
            self.assertIsInstance(exp.output_writer, csv.DictWriter)
        finally:
            exp.output_file.close()

    def test_close_output_file(self):
        model = self.app.model
        exp = self.make_exporter(model_class=model.Setting)

        self.assertIsNone(exp.output_file)
        self.assertIsNone(exp.output_writer)
        exp.open_output_file()
        self.assertIsNotNone(exp.output_file)
        self.assertIsNotNone(exp.output_writer)
        exp.close_output_file()
        self.assertIsNone(exp.output_file)
        self.assertIsNone(exp.output_writer)

    def test_coerce_csv(self):
        model = self.app.model

        # string value
        exp = self.make_exporter(model_class=model.Setting)
        result = exp.coerce_csv({"name": "foo", "value": "bar"})
        self.assertEqual(result, {"name": "foo", "value": "bar"})

        # null value converts to empty string
        result = exp.coerce_csv({"name": "foo", "value": None})
        self.assertEqual(result, {"name": "foo", "value": ""})

        # float value passed thru as-is
        result = exp.coerce_csv({"name": "foo", "value": 12.34})
        self.assertEqual(result, {"name": "foo", "value": 12.34})
        self.assertIsInstance(result["value"], float)

    def test_update_target_object(self):
        model = self.app.model
        exp = self.make_exporter(model_class=model.Setting)

        exp.setup()

        with patch.object(exp, "output_writer") as output_writer:

            # writer is called for normal run
            data = {"name": "foo", "value": "bar"}
            exp.update_target_object(None, data)
            output_writer.writerow.assert_called_once_with(data)

            # but not called for dry run
            output_writer.writerow.reset_mock()
            with patch.object(self.handler, "dry_run", new=True):
                exp.update_target_object(None, data)
                output_writer.writerow.assert_not_called()

        exp.teardown()


class MockMixinExporter(mod.FromSqlalchemyToCsvMixin, FromWutta, mod.ToCsv):
    pass


class TestFromSqlalchemyToCsvMixin(DataTestCase):

    def setUp(self):
        self.setup_db()
        self.handler = ExportHandler(self.config)

    def make_exporter(self, **kwargs):
        kwargs.setdefault("handler", self.handler)
        return MockMixinExporter(self.config, **kwargs)

    def test_model_title(self):
        model = self.app.model
        exp = self.make_exporter(source_model_class=model.Setting)

        # default comes from model class
        self.assertEqual(exp.get_model_title(), "Setting")

        # but can override
        exp.model_title = "Widget"
        self.assertEqual(exp.get_model_title(), "Widget")

    def test_get_simple_fields(self):
        model = self.app.model
        exp = self.make_exporter(source_model_class=model.Setting)

        # default comes from model class
        self.assertEqual(exp.get_simple_fields(), ["name", "value"])

        # but can override
        exp.simple_fields = ["name"]
        self.assertEqual(exp.get_simple_fields(), ["name"])

        # no default if no model class
        exp = self.make_exporter()
        self.assertEqual(exp.get_simple_fields(), [])

    def test_normalize_source_object(self):
        model = self.app.model
        exp = self.make_exporter(source_model_class=model.Setting)
        setting = model.Setting(name="foo", value="bar")
        data = exp.normalize_source_object(setting)
        self.assertEqual(data, {"name": "foo", "value": "bar"})

    def test_make_object(self):
        model = self.app.model

        # normal
        exp = self.make_exporter(source_model_class=model.Setting)
        obj = exp.make_object()
        self.assertIsInstance(obj, model.Setting)

        # no model_class
        exp = self.make_exporter()
        self.assertRaises(TypeError, exp.make_object)


class MockMixinHandler(
    mod.FromSqlalchemyToCsvHandlerMixin, FromWuttaHandler, mod.ToCsvHandler
):
    FromImporterBase = FromWutta


class TestFromSqlalchemyToCsvHandlerMixin(DataTestCase):

    def make_handler(self, **kwargs):
        return MockMixinHandler(self.config, **kwargs)

    def test_get_source_model(self):
        with patch.object(
            mod.FromSqlalchemyToCsvHandlerMixin, "define_importers", return_value={}
        ):
            handler = self.make_handler()
            self.assertRaises(NotImplementedError, handler.get_source_model)

    def test_define_importers(self):
        model = self.app.model
        with patch.object(
            mod.FromSqlalchemyToCsvHandlerMixin, "get_source_model", return_value=model
        ):
            handler = self.make_handler()
            importers = handler.define_importers()
            self.assertIn("Setting", importers)
            self.assertTrue(issubclass(importers["Setting"], FromWutta))
            self.assertTrue(issubclass(importers["Setting"], mod.ToCsv))
            self.assertIn("User", importers)
            self.assertIn("Person", importers)
            self.assertIn("Role", importers)

    def test_make_importer_factory(self):
        model = self.app.model
        with patch.object(
            mod.FromSqlalchemyToCsvHandlerMixin, "define_importers", return_value={}
        ):
            handler = self.make_handler()
            factory = handler.make_importer_factory(model.Setting, "Setting")
            self.assertTrue(issubclass(factory, FromWutta))
            self.assertTrue(issubclass(factory, mod.ToCsv))


class TestFromWuttaToCsv(DataTestCase):

    def make_handler(self, **kwargs):
        return mod.FromWuttaToCsv(self.config, **kwargs)

    def test_get_source_model(self):
        handler = self.make_handler()
        self.assertIs(handler.get_source_model(), self.app.model)

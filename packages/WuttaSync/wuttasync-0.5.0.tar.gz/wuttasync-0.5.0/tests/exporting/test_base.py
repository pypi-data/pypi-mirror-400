# -*- coding: utf-8; -*-

from unittest.mock import patch

from wuttjamaican.testing import DataTestCase

from wuttasync.exporting import base as mod, ExportHandler


class TestToFile(DataTestCase):

    def setUp(self):
        self.setup_db()
        self.handler = ExportHandler(self.config)

    def make_exporter(self, **kwargs):
        kwargs.setdefault("handler", self.handler)
        return mod.ToFile(self.config, **kwargs)

    def test_setup(self):
        model = self.app.model

        # output file is opened
        exp = self.make_exporter(model_class=model.Setting)
        self.assertFalse(exp.dry_run)
        with patch.object(exp, "open_output_file") as open_output_file:
            exp.setup()
            open_output_file.assert_called_once_with()

        # but not if in dry run mode
        with patch.object(self.handler, "dry_run", new=True):
            exp = self.make_exporter(model_class=model.Setting)
            self.assertTrue(exp.dry_run)
            with patch.object(exp, "open_output_file") as open_output_file:
                exp.setup()
                open_output_file.assert_not_called()

    def test_teardown(self):
        model = self.app.model

        # output file is closed
        exp = self.make_exporter(model_class=model.Setting)
        self.assertFalse(exp.dry_run)
        with patch.object(exp, "close_output_file") as close_output_file:
            exp.teardown()
            close_output_file.assert_called_once_with()

        # but not if in dry run mode
        with patch.object(self.handler, "dry_run", new=True):
            exp = self.make_exporter(model_class=model.Setting)
            self.assertTrue(exp.dry_run)
            with patch.object(exp, "close_output_file") as close_output_file:
                exp.teardown()
                close_output_file.assert_not_called()

    def test_get_output_file_path(self):
        model = self.app.model
        exp = self.make_exporter(model_class=model.Setting)

        # output path must be set
        self.assertRaises(ValueError, exp.get_output_file_path)

        # path is guessed from dir+filename
        path1 = self.write_file("data1.txt", "")
        exp.output_file_path = self.tempdir
        exp.output_file_name = "data1.txt"
        self.assertEqual(exp.get_output_file_path(), path1)

        # path can be explicitly set
        path2 = self.write_file("data2.txt", "")
        exp.output_file_path = path2
        self.assertEqual(exp.get_output_file_path(), path2)

    def test_get_output_file_name(self):
        model = self.app.model
        exp = self.make_exporter(model_class=model.Setting)

        # name cannot be guessed
        self.assertRaises(NotImplementedError, exp.get_output_file_name)

        # name can be explicitly set
        exp.output_file_name = "data.txt"
        self.assertEqual(exp.get_output_file_name(), "data.txt")

    def test_open_output_file(self):
        model = self.app.model
        exp = self.make_exporter(model_class=model.Setting)
        self.assertRaises(NotImplementedError, exp.open_output_file)

    def test_close_output_file(self):
        model = self.app.model
        exp = self.make_exporter(model_class=model.Setting)

        path = self.write_file("data.txt", "")
        with open(path, "wt") as f:
            exp.output_file = f
            with patch.object(f, "close") as close:
                exp.close_output_file()
                close.assert_called_once_with()

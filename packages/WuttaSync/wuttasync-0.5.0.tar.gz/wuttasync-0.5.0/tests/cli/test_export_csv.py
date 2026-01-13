# -*- coding: utf-8; -*-

from unittest import TestCase
from unittest.mock import MagicMock, patch

from wuttasync.cli import export_csv as mod, ImportCommandHandler


class TestExportCsv(TestCase):

    def test_basic(self):
        params = {
            "models": [],
            "create": True,
            "update": True,
            "delete": False,
            "dry_run": True,
        }
        ctx = MagicMock(params=params)
        with patch.object(ImportCommandHandler, "run") as run:
            mod.export_csv(ctx)
            run.assert_called_once_with(ctx)

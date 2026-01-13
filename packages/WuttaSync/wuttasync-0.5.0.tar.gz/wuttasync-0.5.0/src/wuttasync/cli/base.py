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
``wutta import-csv`` command
"""

import inspect
import logging
import sys
from pathlib import Path
from typing import List, Optional
from typing_extensions import Annotated

import makefun
import rich
import typer

from wuttjamaican.app import GenericHandler
from wuttasync.importing import ImportHandler, FromFileHandler
from wuttasync.exporting import ToFileHandler


log = logging.getLogger(__name__)


class ImportCommandHandler(GenericHandler):
    """
    This is the :term:`handler` responsible for import/export command
    line runs.

    Normally, the command (actually :term:`subcommand`) logic will
    create this handler and call its :meth:`run()` method.

    This handler does not know how to import/export data, but it knows
    how to make its :attr:`import_handler` do it.  Likewise, the
    import handler is not "CLI-aware" - so this provides the glue.

    :param import_handler: During construction, caller can specify the
       :attr:`import_handler` as any of:

       * import handler instance
       * import handler factory (e.g. class)
       * import handler :term:`spec`

    :param key: Optional :term:`import/export key` to use for handler
       lookup.  Only used if ``import_handler`` param is not set.

    Typical usage for custom commands will be to provide the spec::

       handler = ImportCommandHandler(
           config, "poser.importing.foo:FromFooToPoser"
       )

    Library authors may prefer to use the import/export key; this lets
    the command work with any designated handler::

       handler = ImportCommandHandler(
           config, key="import.to_poser.from_foo"
       )

    See also
    :meth:`~wuttasync.app.WuttaSyncAppProvider.get_import_handler()`
    which does the lookup by key.
    """

    import_handler = None
    """
    Reference to the :term:`import handler` instance, which is to be
    invoked when command runs.  See also :meth:`run()`.
    """

    def __init__(self, config, import_handler=None, key=None):
        super().__init__(config)

        if import_handler:
            if isinstance(import_handler, ImportHandler):
                self.import_handler = import_handler
            elif callable(import_handler):
                self.import_handler = import_handler(self.config)
            else:  # spec
                factory = self.app.load_object(import_handler)
                self.import_handler = factory(self.config)

        elif key:
            self.import_handler = self.app.get_import_handler(key, require=True)

    def run(self, ctx, progress=None):  # pylint: disable=unused-argument
        """
        Run the import/export job(s) based on command line params.

        This mostly just calls
        :meth:`~wuttasync.importing.handlers.ImportHandler.process_data()`
        for the :attr:`import_handler`.

        Unless ``--list-models`` was specified on the command line in
        which case we do :meth:`list_models()` instead.

        :param ctx: :class:`typer.Context` instance.

        :param progress: Optional progress indicator factory.
        """

        # maybe just list models and bail
        if ctx.params.get("list_models"):
            self.list_models(ctx.params)
            return

        # otherwise we'll (hopefully) process some data
        log.debug("using handler: %s", self.import_handler.get_spec())

        # but first, some extra checks for certain file-based
        # handlers.  this must be done here, because these CLI params
        # are not technically required (otherwise typer would handle
        # this instead of us here).  and that is because we want to
        # allow user to specify --list without needing to also specify
        # --input or --output
        if isinstance(self.import_handler, FromFileHandler):
            if not ctx.params.get("input_file_path"):
                rich.print(
                    "\n[bold yellow]must specify --input folder/file path[/bold yellow]\n",
                    file=sys.stderr,
                )
                sys.exit(1)
        elif isinstance(self.import_handler, ToFileHandler):
            if not ctx.params.get("output_file_path"):
                rich.print(
                    "\n[bold yellow]must specify --output folder/file path[/bold yellow]\n",
                    file=sys.stderr,
                )
                sys.exit(1)

        # all params from caller will be passed along
        kw = dict(ctx.params)

        # runas user and comment also, but they come from root command
        if username := ctx.parent.params.get("runas_username"):
            kw["runas_username"] = username
        if comment := ctx.parent.params.get("comment"):
            kw["transaction_comment"] = comment

        # sort out which models to process
        models = kw.pop("models", None)
        if not models:
            models = list(self.import_handler.importers)
        log.debug(
            "%s %s for models: %s",
            self.import_handler.actioning,
            self.import_handler.get_title(),
            ", ".join(models),
        )

        # process data
        log.debug("params are: %s", kw)
        self.import_handler.process_data(*models, **kw)

    def list_models(self, params):  # pylint: disable=unused-argument
        """
        Query the :attr:`import_handler`'s supported target models and
        print the info to stdout.

        This is what happens when command line has ``--list-models``.
        """
        sys.stdout.write("\nALL MODELS:\n")
        sys.stdout.write("==============================\n")
        for key in self.import_handler.importers:
            sys.stdout.write(key)
            sys.stdout.write("\n")
        sys.stdout.write("==============================\n")
        sys.stdout.write(f"for {self.import_handler.get_title()}\n\n")


def import_command_template(  # pylint: disable=unused-argument,too-many-arguments,too-many-positional-arguments,too-many-locals
    models: Annotated[
        Optional[List[str]],
        typer.Argument(
            help="Target model(s) to process.  Specify one or more, "
            "or omit to process default models."
        ),
    ] = None,
    list_models: Annotated[
        bool,
        typer.Option(
            "--list-models", "-l", help="List available target models and exit."
        ),
    ] = False,
    create: Annotated[
        bool,
        typer.Option(
            help="Allow new target records to be created.  " "See aso --max-create."
        ),
    ] = True,
    update: Annotated[
        bool,
        typer.Option(
            help="Allow existing target records to be updated.  "
            "See also --max-update."
        ),
    ] = True,
    delete: Annotated[
        bool,
        typer.Option(
            help="Allow existing target records to be deleted.  "
            "See also --max-delete."
        ),
    ] = False,
    fields: Annotated[
        str,
        typer.Option(
            "--fields", help="List of fields to process.  See also --exclude and --key."
        ),
    ] = None,
    excluded_fields: Annotated[
        str,
        typer.Option(
            "--exclude", help="List of fields *not* to process.  See also --fields."
        ),
    ] = None,
    keys: Annotated[
        str,
        typer.Option(
            "--key",
            "--keys",
            help="List of fields to use as record key/identifier.  "
            "See also --fields.",
        ),
    ] = None,
    max_create: Annotated[
        int,
        typer.Option(
            help="Max number of target records to create (per model).  "
            "See also --create."
        ),
    ] = None,
    max_update: Annotated[
        int,
        typer.Option(
            help="Max number of target records to update (per model).  "
            "See also --update."
        ),
    ] = None,
    max_delete: Annotated[
        int,
        typer.Option(
            help="Max number of target records to delete (per model).  "
            "See also --delete."
        ),
    ] = None,
    max_total: Annotated[
        int,
        typer.Option(
            help="Max number of *any* target record changes which may occur (per model)."
        ),
    ] = None,
    warnings: Annotated[
        bool,
        typer.Option(
            "--warn",
            "-W",
            help="Expect no changes; warn (email the diff) if any occur.",
        ),
    ] = False,
    warnings_recipients: Annotated[
        str,
        typer.Option(
            "--recip",
            "--recips",
            help="Override the recipient(s) for diff warning email.",
        ),
    ] = None,
    warnings_max_diffs: Annotated[
        int,
        typer.Option(
            "--max-diffs",
            help="Max number of record diffs to show (per model) in warning email.",
        ),
    ] = 15,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run", help="Go through the motions, but rollback the transaction."
        ),
    ] = False,
):
    """
    Stub function which provides a common param signature; used with
    :func:`import_command()`.
    """


def import_command(fn):
    """
    Decorator for import/export commands.  Adds common params based on
    :func:`import_command_template()`.

    To use this, e.g. for ``poser import-foo`` command::

       from poser.cli import poser_typer
       from wuttasync.cli import import_command, ImportCommandHandler

       @poser_typer.command()
       @import_command
       def import_foo(
               ctx: typer.Context,
               **kwargs
       ):
           \"""
           Import data from Foo API to Poser DB
           \"""
           config = ctx.parent.wutta_config
           handler = ImportCommandHandler(
               config, import_handler='poser.importing.foo:FromFooToPoser')
           handler.run(ctx.params)

    See also :class:`ImportCommandHandler`.
    """
    original_sig = inspect.signature(fn)
    reference_sig = inspect.signature(import_command_template)

    params = list(original_sig.parameters.values())
    for i, param in enumerate(reference_sig.parameters.values()):
        params.insert(i + 1, param)

    # remove the **kwargs param
    params.pop(-1)

    final_sig = original_sig.replace(parameters=params)
    return makefun.create_function(final_sig, fn)


def file_export_command_template(  # pylint: disable=unused-argument
    # nb. technically this is required, but not if doing --list
    # (so we cannot mark it required here, for that reason)
    output_file_path: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            exists=True,
            file_okay=True,
            dir_okay=True,
            help="Path to output folder.  Or full path to output file "
            "if only running one target model.",
        ),
    ] = None,
):
    """
    Stub function to provide signature for exporter commands which
    produce data file(s) as output.  Used with
    :func:`file_export_command`.
    """


def file_export_command(fn):
    """
    Decorator for file export commands.  Adds common params based on
    :func:`file_export_command_template`.
    """
    original_sig = inspect.signature(fn)
    plain_import_sig = inspect.signature(import_command_template)
    file_export_sig = inspect.signature(file_export_command_template)
    desired_params = list(plain_import_sig.parameters.values()) + list(
        file_export_sig.parameters.values()
    )

    params = list(original_sig.parameters.values())
    for i, param in enumerate(desired_params):
        params.insert(i + 1, param)

    # remove the **kwargs param
    params.pop(-1)

    final_sig = original_sig.replace(parameters=params)
    return makefun.create_function(final_sig, fn)


def file_import_command_template(  # pylint: disable=unused-argument
    # nb. technically this is required, but not if doing --list
    # (so we cannot mark it required here, for that reason)
    input_file_path: Annotated[
        Path,
        typer.Option(
            "--input",
            "-i",
            exists=True,
            file_okay=True,
            dir_okay=True,
            help="Path to input folder.  Or full path to input file "
            "if only running one target model.",
        ),
    ] = None,
):
    """
    Stub function to provide signature for import/export commands
    which require input file.  Used with
    :func:`file_import_command()`.
    """


def file_import_command(fn):
    """
    Decorator for import/export commands which require input file.
    Adds common params based on
    :func:`file_import_command_template()`.

    To use this, it's the same method as shown for
    :func:`import_command()` except in this case you would use the
    ``file_import_command`` decorator.
    """
    original_sig = inspect.signature(fn)
    plain_import_sig = inspect.signature(import_command_template)
    file_import_sig = inspect.signature(file_import_command_template)
    desired_params = list(plain_import_sig.parameters.values()) + list(
        file_import_sig.parameters.values()
    )

    params = list(original_sig.parameters.values())
    for i, param in enumerate(desired_params):
        params.insert(i + 1, param)

    # remove the **kwargs param
    params.pop(-1)

    final_sig = original_sig.replace(parameters=params)
    return makefun.create_function(final_sig, fn)

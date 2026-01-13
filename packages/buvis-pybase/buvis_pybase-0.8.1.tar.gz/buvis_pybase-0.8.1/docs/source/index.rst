buvis-pybase Documentation
==========================

Foundation library for BUVIS Python projects. Provides configuration management,
filesystem utilities, adapters for external tools, and string manipulation.

Getting Started
---------------

**Configuration** is the recommended entry point. It defines how your tools load
settings from CLI arguments, environment variables, YAML files, and defaults.

Quick Example
~~~~~~~~~~~~~

.. code-block:: python

    import click
    from buvis.pybase.configuration import buvis_options, get_settings

    @click.command()
    @buvis_options
    @click.pass_context
    def main(ctx: click.Context) -> None:
        settings = get_settings(ctx)
        if settings.debug:
            click.echo("Debug mode")

See :doc:`configuration` for custom settings classes, YAML configuration,
environment variables, and migration guides.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   configuration
   formatting
   filesystem
   adapters

from typing import Any

import click
from pulp_glue.common.i18n import get_translation
from pulpcore.cli.common.generic import pulp_group

from pulpcore.cli.gem.content import content
from pulpcore.cli.gem.distribution import distribution
from pulpcore.cli.gem.publication import publication
from pulpcore.cli.gem.remote import remote
from pulpcore.cli.gem.repository import repository

translation = get_translation(__package__)
_ = translation.gettext

__version__ = "0.5.3"


@pulp_group(name="gem")
def gem_group() -> None:
    pass


def mount(main: click.Group, **kwargs: Any) -> None:
    gem_group.add_command(content)
    gem_group.add_command(distribution)
    gem_group.add_command(publication)
    gem_group.add_command(remote)
    gem_group.add_command(repository)
    main.add_command(gem_group)

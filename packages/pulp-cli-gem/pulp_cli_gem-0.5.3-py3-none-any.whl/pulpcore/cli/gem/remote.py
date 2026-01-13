import click
from pulp_glue.common.i18n import get_translation
from pulp_glue.gem.context import PulpGemRemoteContext
from pulpcore.cli.common.generic import (
    PulpCLIContext,
    common_remote_create_options,
    common_remote_update_options,
    create_command,
    destroy_command,
    href_option,
    label_command,
    list_command,
    load_json_callback,
    name_option,
    pass_pulp_context,
    pulp_group,
    remote_filter_options,
    remote_lookup_option,
    role_command,
    show_command,
    update_command,
)

translation = get_translation(__package__)
_ = translation.gettext


@pulp_group()
@click.option(
    "-t",
    "--type",
    "remote_type",
    type=click.Choice(["gem"], case_sensitive=False),
    default="gem",
)
@pass_pulp_context
@click.pass_context
def remote(ctx: click.Context, pulp_ctx: PulpCLIContext, remote_type: str) -> None:
    if remote_type == "gem":
        ctx.obj = PulpGemRemoteContext(pulp_ctx)
    else:
        raise NotImplementedError()


lookup_options = [href_option, name_option, remote_lookup_option]
nested_lookup_options = [remote_lookup_option]
gem_remote_options = [
    click.option(
        "--policy", type=click.Choice(["immediate", "on_demand", "streamed"], case_sensitive=False)
    ),
    click.option(
        "--includes",
        callback=load_json_callback,
        help=_("Gem allow list. Dictionary of form 'gem:version-specifier/null'"),
    ),
    click.option(
        "--excludes",
        callback=load_json_callback,
        help=_("Gem block list. Dictionary of form 'gem:version-specifier/null'"),
    ),
    click.option(
        "--prereleases/--no-prereleases", default=None, help=_("Include prereleases in sync")
    ),
]

remote.add_command(list_command(decorators=remote_filter_options))
remote.add_command(show_command(decorators=lookup_options))
remote.add_command(create_command(decorators=common_remote_create_options + gem_remote_options))
remote.add_command(
    update_command(decorators=lookup_options + common_remote_update_options + gem_remote_options)
)
remote.add_command(destroy_command(decorators=lookup_options))
remote.add_command(label_command(decorators=nested_lookup_options))
remote.add_command(role_command(decorators=nested_lookup_options))

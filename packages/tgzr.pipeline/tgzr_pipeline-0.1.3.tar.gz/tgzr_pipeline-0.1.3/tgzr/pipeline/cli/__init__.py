import rich
import rich.table
import click

from .._version import __version__
from ..workspace import Workspace
from .utils import ShortNameGroup


@click.group(
    cls=ShortNameGroup,
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.version_option(version=__version__, prog_name="pipeline")
@click.option("-w", "--workspace", required=True, help="Path to the asset workspace.")
@click.option(
    "-c",
    "--create-workspace",
    is_flag=True,
    default=False,
    help="Create the specified workspace if it doesn't exists.",
)
@click.option(
    "-R",
    "--blessed-repo",
    help="Add a repo and make it the default one to install from.",
)
@click.option(
    "-r",
    "--default-repo",
    multiple=True,
    help="Add a repo and make it the default one to publish to.",
)
@click.pass_context
def pipeline_cli(
    ctx, workspace: str, create_workspace: bool, blessed_repo, default_repo: list[str]
):
    """
    The -R and -r option must be like repo_name=/path/to/repo
    The last of the -r option will be the actual default publish repo.
    """
    ws = Workspace(workspace)
    if create_workspace:
        ws.ensure_exists()

    if blessed_repo:
        try:
            name, path = blessed_repo.split("=")
        except:
            raise click.UsageError(
                f"Syntax error: {blessed_repo!r} is not like xxx=yyy"
            )
        ws.add_repo(name, path, make_blessed=True, make_default=False)

    for repo_option in default_repo:
        try:
            name, path = repo_option.split("=")
        except:
            raise click.UsageError(f"Syntax erro: {repo!r} is not like xxx=yyy")
        ws.add_repo(name, path, make_blessed=False, make_default=True)

    ctx.obj = ws


#
# WORKSPACE
#


@pipeline_cli.group(cls=ShortNameGroup, help="Manage asset workspace.")
def workspace():
    pass


@workspace.command
@click.pass_obj
def rebuild(ws: Workspace):
    print("REBUILD", ws)
    ws.ensure_exists(force_build=True)


@workspace.command
# @click.option("--requirements", nargs=0, required=True)
@click.argument("requirements", nargs=-1)
@click.pass_obj
def add_external_packages(ws: Workspace, requirements):
    """
    Make external packages (non assets) available as asset
    dependencies.

    \b
    Accepted forms of requirements:
        my_lib==1.2.3
        my_lib>=1.2.3
        my_lib<=1.2.3
        my_lib>=1.2.3<2.0
        ...

    """
    if not requirements:
        raise click.UsageError("Please provide at least on requirement.")
    ws.add_extenal_packages(*requirements)


#
# REPO
#


@pipeline_cli.group(cls=ShortNameGroup, help="Manage asset repositories.")
def repo():
    pass


@repo.command(help="Manage asset repositories.")
@click.pass_obj
def show(ws: Workspace):
    default = ws._default_repo_name
    blessed = ws._blessed_repo_name

    table = rich.table.Table("name", "path", "blessed", "default")
    for name, path in ws._default_repos.items():
        table.add_row(
            name, path, name == blessed and "*" or "", name == default and "*" or ""
        )

    rich.print(table)


@repo.command(help="Manage asset repositories.")
@click.argument("name")
@click.argument("path")
@click.option(
    "-B",
    "--blessed",
    required=False,
    default=False,
    help="Make this repo the default one to install from. Defaults to False.",
)
@click.option(
    "-d",
    "--default",
    required=False,
    default=True,
    help="Make this repo the default one to publish to. Defaults to True.",
)
@click.pass_obj
def add(ws: Workspace, name, path, make_blessed, make_default):
    # NB: these are not saved to a config file or anything, maybe we should?
    # Anyway, as of right now there's no purpose in using this cmd ¯\_(ツ)_/¯
    ws.add_repo(name, path, make_blessed=make_blessed, make_default=make_default)


#
# ASSET
#


@pipeline_cli.group(cls=ShortNameGroup, help="Manage assets")
def asset():
    pass


@asset.command
@click.argument("name")
@click.option(
    "-T",
    "--asset-type",
    default="Asset",
    help="The type asset to create, like Asset or ToolAsset (depends on the installed asset plugins)",
)
@click.option(
    "-d",
    "--default-repo",
    help="The name of the default repo to publish to.",
)
@click.option(
    "-r",
    "--repo",
    multiple=True,
    help='Extra repo for this asset (like "-r repo-name=repo/path)"',
)
@click.pass_obj
def create(
    ws: Workspace, asset_type: str, name: str, default_repo: str, repo: list[str]
):
    ws.create_asset(asset_type, name, default_repo=default_repo, *repo)


@asset.command
@click.argument("name")
@click.pass_obj
def rebuid_pyproject(ws: Workspace, name: str):
    """Rebuild the asset pyproject file, bump the version micro and (re)install."""
    ws.rebuid_pyproject(name)


@asset.command
@click.argument("name")
@click.argument("tags", nargs=-1)
@click.pass_obj
def tag(ws: Workspace, name: str, tags: list[str]):
    """Add tags to asset."""
    if not tags:
        click.echo("No tags given, nothing to do.")
    ws.tag_asset(name, *tags)


@asset.command
@click.argument("name")
@click.argument("requirements", nargs=-1)
@click.pass_obj
def add_input(ws: Workspace, name, requirements):
    if not requirements:
        click.echo("No requirements given, nothing to do.")
    ws.add_inputs(name, *requirements)


@asset.command(help=f"\b\n {Workspace.bump_asset.__doc__}")
@click.argument("name")
@click.argument("bump", required=False, default="minor")
@click.pass_obj
def bump(ws: Workspace, name, bump):
    ws.bump_asset(name, bump)


@asset.command
@click.argument("name")
@click.option(
    "-b",
    "--bump",
    default="minor",
    help=(
        "The part of the version to bump, like "
        "'major', 'minor', 'micro', 'alpha', 'rc' or a combination like 'minor,rc'. "
        "Defaults to 'minor'."
    ),
)
@click.pass_obj
def build(ws: Workspace, name, bump):
    ws.build_asset(name, bump)


@asset.command
@click.argument("name")
@click.option(
    "-r",
    "--repo",
    required=False,
    default=None,
    help="Name of repo to upload to (overrides the asset configuration).",
)
@click.pass_obj
def publish(ws: Workspace, name, repo: str | None):
    ws.publish_asset(name, repo)

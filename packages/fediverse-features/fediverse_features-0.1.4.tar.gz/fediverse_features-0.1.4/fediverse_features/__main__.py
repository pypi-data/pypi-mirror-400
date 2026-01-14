import click
import os


from .latest_package import determine_latest_tag

from .gitignore import ensure_in_gitignore

from . import fediverse_features_archive, load_config


@click.group(invoke_without_command=True)
@click.option("--list", is_flag=True, default=False, help="Lists available features")
@click.option("--tag", help="Overwrites the default from fediverse-features.toml")
@click.pass_context
def features(ctx, list, tag):
    if ctx.invoked_subcommand:
        return
    config = load_config()
    if not tag:
        tag = config.tag

    with fediverse_features_archive(tag) as archive:
        if list:
            print("Available feature files")
            for filename in archive.namelist():
                if filename.endswith(".feature"):
                    print(filename)
        else:
            for name in config.features:
                existed = os.path.exists(config.target + name)
                file = archive.extract(name, config.target)
                method = "overwrote" if existed else "added"
                print(f"{method} {file}")


@features.command()
def gitignore():
    """Adds target directory to .gitignore if not present"""
    ensure_in_gitignore("features/fediverse-features")


@features.command()
@click.option("--filename", default="fediverse-features.toml")
def new(filename):
    """Creates a new fediverse-features.toml file"""
    latest_tag = determine_latest_tag()

    if os.path.exists(filename):
        print("file already exists")
        exit(1)

    with open(filename, "w") as fp:
        fp.write(f"""tag = "{latest_tag}"

features = []
""")


@features.command()
def latest():
    """Determines the latest tag"""

    current_tag = load_config().tag
    latest_tag = determine_latest_tag()
    print(f"The latest tag is: {latest_tag}")

    if latest_tag != current_tag:
        print(f"The current tag is {current_tag}")


if __name__ == "__main__":
    features()

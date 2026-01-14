import tomllib
from click.testing import CliRunner
from .__main__ import features


def test_features_new(tmp_path):
    filename = tmp_path / "features.toml"
    runner = CliRunner()
    runner.invoke(features, ["new", "--filename", filename])

    with open(filename, "rb") as f:
        data = tomllib.load(f)

    assert "tag" in data

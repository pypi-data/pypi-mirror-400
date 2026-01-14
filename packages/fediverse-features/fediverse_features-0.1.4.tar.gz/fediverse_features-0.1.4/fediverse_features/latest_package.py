import requests
import semver

codeberg_url = "https://codeberg.org/api/v1/packages/helge"


def determine_latest_tag(package_name="fediverse-features") -> str:
    response = requests.get(codeberg_url)

    package_tags = [x["version"] for x in response.json() if x["name"] == package_name]
    package_tags = sorted(package_tags, key=lambda x: semver.Version.parse(x))

    return package_tags[-1]

import json
import os

from cscs_tools.version.models.entities.version import Version

script_dir = os.path.dirname(__file__)


class VersionFileRepository:
    def __init__(self, file="version.json"):
        self.path = f"{script_dir}/../../../../{file}"

    def get_version(self):
        if not os.path.isfile(self.path):
            raise VersionFileNotFoundError(
                f"""
Version file not found at the root directory.
Expected a JSON file like: 
{{
    \"major\": 0, 
    \"minor\": 2, 
    \"patch\": 1, 
    \"inherit\": true
}}

Either create it at your project root or specify its path like:

service = VersionService(file='path/to/version.json')
"""
            )

        try:
            with open(self.path) as json_file:
                version_dict = json.load(json_file)
                return Version(version_dict)
        except FileNotFoundError:
            return None

    def save(self, version):
        with open(self.path, "w") as json_file:
            json.dump(version.__dict__, json_file)
        return True


class VersionFileNotFoundError(Exception):
    """Custom exception for missing version file."""
    pass